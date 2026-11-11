import json, re, datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment, NamedStyle
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.drawing.image import Image
from openpyxl.utils import get_column_letter

d = json.load(open('/home/claude/inv.json'))
SK, GROUPS, EXTRA, KNOWN = d['skus'], d['groups'], d['order_extra'], d['known']
VER = re.search(r'version: "([^"]+)"', open('/home/claude/xploreforms/fieldkit/version.js').read()).group(1)

ORDER_PICK = ["ROUTER","HIGH-GAIN","ONT","DROP CABLE","STB","AERIAL","AZEL","TRIMAST","ANTENNA"]
ORDER_FAMILY_ONLY = ["5G CPE","CAT12 2.5GHZ","CAT12 3.5GHZ"]
ORDER_HIDE = ["CAT4 3.5GHZ"]
EQUIP = {"5G CPE":"Radio (CPE)","HIGH-GAIN":"Radio (CPE)","CAT4 3.5GHZ":"Radio (CPE)","CAT12 2.5GHZ":"Radio (CPE)","CAT12 3.5GHZ":"Radio (CPE)",
 "ROUTER":"Router","CUBE":"XWH extender","MESH":"XWH extender","ONT":"ONT","STB":"XTV box","MODEM":"Modem","HT2000":"Modem","HT3000":"Modem",
 "1 WATT RADIO":"TRIA","2 WATT RADIO":"TRIA","ETRIA":"TRIA","DROP CABLE":"Drop","NID":"NID","J ARM":"Mount","SURGE":"Surge",
 "AZEL":"AzEl","TRIMAST":"Trimast","ANTENNA":"Dish"}
PHOTO = {"Radio (CPE)":"CPE SN","Router":"XWR SN","XWH extender":"XWH SN","ONT":"ONT SN","XTV box":"XTV SN","Modem":"Modem SN","TRIA":"TRIA SN"}
EQUIP_FK = {"FK-BIPOD":"Mount","FK-GABLE":"Mount","FK-TRIPOD":"Mount","FK-POLE10":"Mount (pole)","FK-POLE5":"Mount (pole)","FK-SIDESTAYS":"Mount (side stays)","FK-SATPOLE":"Mount","FK-DROP1000":"Drop"}

def how(s):
    if s.get('hidden'): return "Hidden (old entry)"
    if s['fam'] in ORDER_HIDE: return "Not orderable (CAT4)"
    if re.match(r'^NLA\b', s.get('desc') or '', re.I): return "Not orderable (NLA: no longer available)"
    if s.get('noOrder'): return "Not orderable (Field Kit item)"
    if s['fam'] in ORDER_PICK: return "Tech must choose a model"
    if s['fam'] in ORDER_FAMILY_ONLY: return "By family only (no model choice)"
    return "Ordered as this item"

GREEN, DARK, ORANGE, MUTED, HAIR = "5CBC5D", "012929", "FFB21C", "4D6969", "E5E5E5"
wb = Workbook()
normal = wb._named_styles['Normal']; normal.font = Font(name="Poppins", size=10, color=DARK)
hair = Border(bottom=Side(style="hair", color=HAIR))
box = Side(style="thin", color=GREEN); inp = Border(left=box, right=box, top=box, bottom=box)
HF = Font(name="Poppins SemiBold", size=10, color="FFFFFF"); HFILL = PatternFill("solid", fgColor=DARK)
BF = Font(name="Poppins", size=10, color=DARK); MF = Font(name="Poppins", size=10, color=MUTED)
wrapT = Alignment(vertical="top", wrap_text=True); top = Alignment(vertical="top")

# ---------------- Items ----------------
ws = wb.active; ws.title = "Items"
ws.sheet_properties.tabColor = DARK
cols = [("Part number (SKU)",20,"Do not change: entries already logged use it"),("Plain name (shown to techs)",34,"EDIT"),("Category (Field Stock)",24,"EDIT"),
        ("Product family (system)",16,""),("Family name (plain, used for ordering)",28,""),("System description",52,""),("Serialized",11,""),
        ("Technology codes",24,""),("Equipment type",18,""),("Scan photo label",15,""),("Ordered how",34,""),("Known serials",12,""),("In your workbooks",20,""),("Your notes",40,"EDIT")]
for i,(h,w,_) in enumerate(cols,1):
    c = ws.cell(1,i,h); c.font=HF; c.fill=HFILL; c.alignment=Alignment(vertical="center",wrap_text=True)
    ws.column_dimensions[get_column_letter(i)].width = w
ws.row_dimensions[1].height = 32
EDITCOLS = {2,3,14}
for r,s in enumerate(SK,2):
    eq = EQUIP.get(s['fam']) or EQUIP_FK.get(s['id']) or ("—" if not s['fam'] else "")
    vals = [s['id'], s['name'], s['group'], s['fam'] or "—", s['famName'] or "—", s.get('desc') or "", "Yes" if s['serial'] else "No",
            ", ".join(s.get('platforms') or []) or "—", eq or "—", PHOTO.get(eq,"—"), how(s), KNOWN.get(s['id'],0),
            "No (added by Field Kit)" if s.get('extra') else "Yes", ""]
    for i,v in enumerate(vals,1):
        c = ws.cell(r,i,v); c.font = MF if v=="—" else BF; c.alignment = wrapT if i in (2,6,11,14) else top
        c.border = inp if i in EDITCOLS else hair
    ws.cell(r,12).number_format = '#,##0;(#,##0);"—"'; ws.cell(r,12).alignment = Alignment(vertical="top",horizontal="right")
last = len(SK)+1
ws.freeze_panes = "C2"; ws.auto_filter.ref = f"A1:{get_column_letter(len(cols))}{last}"
# category picker (typing a new one is allowed)
dv = DataValidation(type="list", formula1="=Categories!$A$2:$A$25", allow_blank=True, showErrorMessage=False)
dv.promptTitle="Category"; dv.prompt="Pick one, or type a new category (then add it on the Categories tab)."; dv.showInputMessage=True
ws.add_data_validation(dv); dv.add(f"C2:C{last+60}")

# ---------------- Categories ----------------
wc = wb.create_sheet("Categories"); wc.sheet_properties.tabColor = DARK
for i,(h,w) in enumerate([("Category (in the order Field Stock lists them)",46),("Items",10)],1):
    c=wc.cell(1,i,h); c.font=HF; c.fill=HFILL; wc.column_dimensions[get_column_letter(i)].width=w
for r,g in enumerate(GROUPS,2):
    a=wc.cell(r,1,g); a.font=BF; a.border=inp
    b=wc.cell(r,2,f'=COUNTIF(Items!$C$2:$C${last+60},A{r})'); b.font=BF; b.border=hair; b.alignment=Alignment(horizontal="right")
for r in range(len(GROUPS)+2, 17):       # spare rows for new categories
    wc.cell(r,1).border=inp; wc.cell(r,1).font=BF
    b=wc.cell(r,2,f'=IF(A{r}="","",COUNTIF(Items!$C$2:$C${last+60},A{r}))'); b.font=BF; b.border=hair; b.alignment=Alignment(horizontal="right")
wc.cell(18,1,"Add a new category in the first empty green box above. Move a row up or down to change the order.").font=MF
wc.freeze_panes="A2"

# ---------------- Order-only lines ----------------
wo = wb.create_sheet("Order-only lines"); wo.sheet_properties.tabColor = DARK
oh=[("Product family (system)",20),("Family name (plain)",22),("Plain name",44),("Label inventory knows it by",58),("Your notes",40)]
for i,(h,w) in enumerate(oh,1):
    c=wo.cell(1,i,h); c.font=HF; c.fill=HFILL; wo.column_dimensions[get_column_letter(i)].width=w
for r,x in enumerate(EXTRA,2):
    fam_name = x.get('famName') or next((s['famName'] for s in SK if s['fam']==x['fam']), x['fam'])
    for i,v in enumerate([x['fam'], fam_name, x['name'], x['label'], ""],1):
        c=wo.cell(r,i,v); c.font=BF; c.border = inp if i in (3,5) else hair; c.alignment=wrapT
wo.cell(len(EXTRA)+3,1,"These can be ordered on a Manual Order Request but are not tracked as stock in Field Stock.").font=MF
wo.freeze_panes="A2"

# ---------------- Read me (first tab, summary) ----------------
wr = wb.create_sheet("Read me", 0); wr.sheet_properties.tabColor = GREEN; wr.sheet_view.showGridLines = False
wr.column_dimensions['A'].width = 34; wr.column_dimensions['B'].width = 84; wr.column_dimensions['C'].width = 24
wr['A1'] = "Field Kit inventory list"; wr['A1'].font = Font(name="Poppins", bold=True, size=16, color=DARK)
wr['A2'] = f"Exported {datetime.date.today():%b %d, %Y} from Field Kit {VER}. {len(SK)} items, {len(GROUPS)} categories."; wr['A2'].font = Font(name="Poppins", size=10, color=MUTED)
logo = Image('/mnt/skills/plugins/xplore-brand-artifacts/assets/xplore-logo-secondary-green.png'); logo.width, logo.height = 150, int(150*190/753); wr.add_image(logo, 'C1')
rows = [
 ("How to use this", None),
 ("1. Edit the green-outlined cells", "Plain name, Category and Your notes on the Items tab. Plain names are what techs see everywhere: Field Stock, SAs, scan results, orders."),
 ("2. Leave the part numbers alone", "Entries already logged in Field Stock use them. To add an item, add a row with its part number."),
 ("3. Send it back", "When you're done, give me the file and say \"apply the inventory list\". I'll update Field Kit and test it."),
 ("", None),
 ("What the columns mean", None),
 ("Plain name", "The simple name techs see. Items that share a plain name are one item to techs (e.g. the three Nokia XS-010X ONTs)."),
 ("Category", "Where the item sits in Field Stock's lists. Pick from the list or type a new one."),
 ("Product family / Family name", "How the system groups it. Manual orders are placed by family name."),
 ("Technology codes", "Which networks use it (FTX, FWN, HJ3 and so on), from your equipment workbook. Blank means none given."),
 ("Equipment type / Scan photo label", "The kind of equipment on an SA, and the photo label a scan of it gets (CPE SN, XWR SN and so on)."),
 ("Known serials", "How many real serial numbers from your Serial Lookup workbook are tied to this item."),
 ("In your workbooks", "\"No\" means Field Kit added it itself (mounts, poles, side stays, the 1000 m drop, XTV guides, the HC210 2 W radio)."),
 ("", None),
 ("How each item is ordered today", None),
 ("Tech must choose a model", "Router, 5G High Gain CPE, ONT, Drop cable, TV box, Aerial kit, AzEl, Trimast, Dish. There is no \"any model\"."),
 ("By family only (no model choice)", "5G CPE and LTE CPE – CAT12 (2.5 and 3.5 GHz): ordered by family, inventory sends what they have."),
 ("Ordered as this item", "The family has just this one item."),
 ("Not orderable", "CAT4; items marked NLA (no longer available) such as the Zyxel EMG6726 router; and Field Kit's own mount parts."),
]
r=4
for a,b in rows:
    if b is None and a:
        c=wr.cell(r,1,a); c.font=Font(name="Poppins SemiBold", size=10, color=DARK)
        for col in (1,2): wr.cell(r,col).border=Border(bottom=Side(style="thin",color=GREEN))
    elif a or b:
        wr.cell(r,1,a).font=Font(name="Poppins SemiBold", size=10, color=DARK); wr.cell(r,1).alignment=wrapT
        wr.cell(r,2,b).font=BF; wr.cell(r,2).alignment=wrapT
    r+=1
for sh in wb.worksheets:   # prints one page wide, landscape
    sh.page_setup.orientation = 'landscape'; sh.page_setup.fitToWidth = 1; sh.page_setup.fitToHeight = 0; sh.sheet_properties.pageSetUpPr.fitToPage = True
wb.save('/mnt/user-data/outputs/FieldKit_Inventory_List.xlsx'); print('saved', len(SK), 'items, last row', last)
