import json
T=json.load(open('work/trans.json')); ph=json.load(open('work/photos.json')); bg=json.load(open('work/bgs.json'))
photos={}
for k,v in ph.items():
    a,b,c,d,e,f=v['m']
    if v['flip']:
        w=v['w']; m=[-a,-b,c,d,a*w+e,b*w+f]
    else: m=[a,b,c,d,e,f]
    photos[k]={'f':v['file'],'w':v['w'],'h':v['h'],'m':[round(x,6) for x in m]}
bgl=[bg['S%d'%i] for i in range(1,10)]
html=open('work/tpl.html').read()
html=html.replace('__TRANS__',json.dumps(T,separators=(',',':'))).replace('__PHOTOS__',json.dumps(photos)).replace('__BGS__',json.dumps(bgl))
open('index.html','w').write(html)
print(len(html))
