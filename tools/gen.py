import json
T=json.load(open('tools/trans.json')); ph=json.load(open('tools/photos.json')) 
photos={}
for k,v in ph.items():
    a,b,c,d,e,f=v['m']
    if v['flip']:
        w=v['w']; m=[-a,-b,c,d,a*w+e,b*w+f]
    else: m=[a,b,c,d,e,f]
    photos[k]={'f':v['file'],'w':v['w'],'h':v['h'],'m':[round(x,6) for x in m]}
html=open('tools/tpl.html').read()
IDLE=json.load(open('tools/idle.json'))
html=html.replace('__IDLE__',json.dumps(IDLE,separators=(',',':')))
html=html.replace('__TRANS__',json.dumps(T,separators=(',',':'))).replace('__PHOTOS__',json.dumps(photos))
open('index.html','w').write(html)
print(len(html))
