import zipfile, re, shutil, sys
src='/mnt/user-data/outputs/FieldKit_Inventory_List.xlsx'; tmp='/home/claude/xl/clean.xlsx'
zin=zipfile.ZipFile(src); zout=zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED)
for it in zin.infolist():
    data=zin.read(it.filename)
    if it.filename=='xl/styles.xml':
        s=data.decode('utf-8')
        s=re.sub(r'<indexedColors>.*?</indexedColors>','',s,flags=re.S)           # legacy colour palette nothing uses
        s=re.sub(r'(<name val=")(Arial|Calibri|Cambria)(")',r'\1Poppins\3',s)       # default fonts of unused built-in styles
        s=s.replace('<bgColor rgb="FF003366"/>','<bgColor rgb="FF012929"/>')               # ignored for solid fills, but keep it on palette
        data=s.encode('utf-8')
    elif it.filename=='xl/theme/theme1.xml':
        s=data.decode('utf-8')
        s=re.sub(r'(<a:latin typeface=")[^"]*(")',r'\1Poppins\2',s)                 # theme heading + body font
        data=s.encode('utf-8')
    zout.writestr(it,data)
zout.close(); shutil.move(tmp,src); print('cleaned')
