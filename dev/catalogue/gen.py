"""Build fieldkit-catalog.js from Curtis's workbooks (FieldKit_Equipment_Catalogue.xlsx, FieldKit_Serial_Lookup.xlsx)
plus the items Field Kit already had that aren't in them."""
import pandas as pd, json, re, subprocess
up='/mnt/user-data/uploads/'
cat=pd.read_excel(up+'FieldKit_Equipment_Catalogue.xlsx','SKU catalogue')
rules=pd.read_excel(up+'FieldKit_Serial_Lookup.xlsx','Recognition rules')
known=pd.read_excel(up+'FieldKit_Serial_Lookup.xlsx','Serial lookup')
old=json.loads(subprocess.check_output(['node','-e','global.window={}; eval(require("fs").readFileSync("/home/claude/cat/old-catalog.js","utf8")); console.log(JSON.stringify(window.FK_CATALOG.SKUS))']))
OLD={s['id']:s for s in old}

FAM={ # system Product Family -> plain family name
 'DROP CABLE':'Drop cable','NID':'NID','ONT':'ONT','5G CPE':'5G CPE','HIGH-GAIN':'5G High Gain CPE',
 'CAT4 3.5GHZ':'LTE CPE – CAT4 3.5 GHz','CAT12 2.5GHZ':'LTE CPE – CAT12 2.5 GHz','CAT12 3.5GHZ':'LTE CPE – CAT12 3.5 GHz',
 'J ARM':'J-Arm','SURGE':'Surge','AZEL':'AzEl','TRIMAST':'Trimast','ANTENNA':'Dish','HT2000':'HT2000 modem','HT3000':'HT3000 modem',
 'MODEM':'SurfBeam 2 modem','1 WATT RADIO':'TRIA - 1 Watt','2 WATT RADIO':'TRIA - 2 Watt','ETRIA':'eTRIA - Viasat',
 'ROUTER':'Router','CUBE':'XWH extender','MESH':'Mesh extender','STB':'TV box'}
def group(fam, name, plats):
    if fam in ('5G CPE','HIGH-GAIN'): return '5G & fixed wireless'
    if fam.startswith('CAT'): return 'LTE'
    if fam in ('ROUTER','CUBE','MESH'): return 'Wi-Fi & routers'
    if fam=='ONT': return 'Fibre ONTs'
    if fam in ('DROP CABLE','NID'): return 'Fibre drops & NIDs'
    if fam=='STB': return 'TV'
    if fam in ('J ARM','SURGE'): return 'Mounts & surge'
    if fam in ('MODEM','ETRIA') or 'Viasat' in name: return 'SurfBeam satellite'
    return 'Hughes satellite'
NAMEFIX={'Next Gent High Gain':'Next Gen High Gain'}
skus=[]
for _,r in cat.iterrows():
    fam=str(r['Product Family']).strip(); pid=str(r['Product Name']).strip(); name=NAMEFIX.get(str(r['Plain language name']).strip(), str(r['Plain language name']).strip())
    plats=[p.strip() for p in str(r['Platforms']).split(',') if re.fullmatch(r'[A-Z0-9]{3}',p.strip())]
    ser=str(r['Serialized']).strip()
    serial = ser=='Yes' if ser in ('Yes','No') else bool(OLD.get(pid,{}).get('serial', True))
    skus.append({'id':pid,'name':name,'desc':str(r['Material Description']).strip(),'fam':fam,'famName':FAM[fam],'group':group(fam,name,plats),'serial':serial,'platforms':plats})
have={s['id'] for s in skus}
# items Field Kit already had that aren't in the workbook: kept (mounts and poles the SA mount choices use, etc.)
EXTRA_FAM={'1507724-1004':('2 WATT RADIO','TRIA - 2 Watt'),'FK-DROP1000':('DROP CABLE','Drop - 1000m - Evolv Dielectric Drop PushLok Tech')}
for o in old:
    if o['id'] in have: continue
    s={'id':o['id'],'name':o['name'],'desc':o['name'],'fam':'','famName':'','group':o['group'].replace('Fiber','Fibre'),'serial':o['serial'],'platforms':[],'extra':True}
    if o.get('hidden'): s['hidden']=True
    if o['id'] in EXTRA_FAM: s['fam'],s['name']=EXTRA_FAM[o['id']]; s['famName']=FAM[s['fam']]
    if o['id'].startswith('FK-') or o['id']=='XTV LEAVE BEHIND': s['noOrder']=True
    skus.append(s)
# workbook order within each group, groups in this order
GROUPS=['5G & fixed wireless','LTE','Wi-Fi & routers','Fibre ONTs','Fibre drops & NIDs','TV','Hughes satellite','SurfBeam satellite','Mounts & surge']
assert all(s['group'] in GROUPS for s in skus), [s for s in skus if s['group'] not in GROUPS]
skus.sort(key=lambda s:GROUPS.index(s['group']))
R=[]
for _,r in rules.iterrows():
    rx=str(r['Serial pattern (regex)']).strip(); ids=[x.strip() for x in str(r['Candidate Product Name(s)']).split(',')]
    assert all(i in {s['id'] for s in skus} for i in ids), ids
    R.append((r['Rule'],rx,ids))
K={}
for _,r in known.iterrows():
    sn=re.sub(r'\s+','',str(r['Serial Number'])).upper(); pid=str(r['Product Name']).strip()
    if pid in {s['id'] for s in skus}: K[sn]=pid
# order-only lines from today's manual order form that aren't stock items (HV2 left off for now)
ORDER_EXTRA=[{'fam':'ONT','name':'Adtran 411','label':'ATX&MTX - ONT - Adtran ONT Total Access 411'},
  {'fam':'REMOTE','famName':'TV remote','name':'Nova universal remote','label':'MTV - REMOTE - REMOTE CONTROL NOVA UNIVERSAL'},
  {'fam':'AERIAL','famName':'Aerial kit','name':'Pushlok Optitap Converter Kit (20)','label':'BBX - AERIAL - Pushlok Optitap Converter Kit (20)'},
  {'fam':'AERIAL','famName':'Aerial kit','name':'AFL FASTConnector SC/APC 900UM & 250UM (100)','label':'BBX - AERIAL - AFL FASTConnector SC/APC 900UM & 250UM (100)'}]
js=['/* Field Kit item catalogue: every stock item, its plain-language name and family, and how serial numbers identify it.',
 '   Built from Curtis\'s FieldKit_Equipment_Catalogue.xlsx and FieldKit_Serial_Lookup.xlsx (inventory exports 2026-11-09).',
 '   id = the SKU (never change an id: entries already logged use it). name = what techs see. desc = the system description.',
 '   fam = the system Product Family; famName = its plain name (manual orders go by family). Items with the same name are one',
 '   item to techs (e.g. the three Nokia XS-010X ONTs). Shared by Field Stock, Field Cam and Field Kit SAs. Edit here only. */',
 '(function () {','var SKUS = [']
js.append(',\n'.join('  '+json.dumps(s,ensure_ascii=False) for s in skus)+'\n];')
js.append('var GROUPS = '+json.dumps(GROUPS,ensure_ascii=False)+';')
js.append('/* serial number patterns (Recognition rules R01–R22): first match wins; more than one item means the tech picks */')
js.append('var SERIAL_RULES = [\n'+'\n'.join(f'  [/{rx}/, {json.dumps(ids)}]'+(',' if i<len(R)-1 else '')+f'   // {rid}' for i,(rid,rx,ids) in enumerate(R))+'\n];')
js.append('/* serial numbers inventory has already seen (Serial lookup): these name the exact item, before any pattern */')
js.append('var KNOWN = '+json.dumps(K,separators=(',',':'))+';')
js.append('/* lines on the manual order form that aren\'t stock items */')
js.append('var ORDER_EXTRA = '+json.dumps(ORDER_EXTRA,ensure_ascii=False)+';')
js.append('''var BY = {}; SKUS.forEach(function (s) { BY[s.id] = s; });
var key = function (v) { return String(v || "").replace(/\\s+/g, "").toUpperCase(); };
/* items a serial could be: known serial first, then the patterns. Items sharing a name count once (the first one). */
function match(serial) {
  var k = key(serial); if (!k) return [];
  if (KNOWN[k] && BY[KNOWN[k]]) return [KNOWN[k]];
  for (var i = 0; i < SERIAL_RULES.length; i++) if (SERIAL_RULES[i][0].test(k)) return oneEach(SERIAL_RULES[i][1].filter(function (id) { return BY[id]; }));
  return [];
}
function oneEach(ids) { var seen = {}; return ids.filter(function (id) { var n = BY[id].name; if (seen[n]) return false; seen[n] = 1; return true; }); }
/* the first item of each name in a list of items (pickers show one entry per name) */
function firstOfName(list) { var seen = {}; return list.filter(function (s) { var n = s.group + "|" + s.name; if (seen[n]) return false; seen[n] = 1; return true; }); }
window.FK_CATALOG = { SKUS: SKUS, GROUPS: GROUPS, SERIAL_RULES: SERIAL_RULES, KNOWN: KNOWN, ORDER_EXTRA: ORDER_EXTRA, match: match, oneEach: oneEach, firstOfName: firstOfName };
})();''')
open('/home/claude/xploreforms/fieldkit/fieldkit-catalog.js','w',encoding='utf-8').write('\n'.join(js)+'\n')
print(len(skus),'items,',len(R),'rules,',len(K),'known serials')
print('new ids:', sorted(have-set(OLD)))
print('kept extras:', [s['id'] for s in skus if s.get('extra')])
