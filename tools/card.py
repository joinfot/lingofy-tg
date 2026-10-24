import urllib.parse, sys, json
CLOUD="fdmj7wxb"
def t(s):
    s=s.replace(',', '%2C').replace('/', '%2F')
    return urllib.parse.quote(s, safe='')
def text(s, font, size, weight, color, x, y, w=None, g="north_west"):
    parts=[]
    if w: parts.append(f"w_{w},c_fit")
    fw=f"_{weight}" if weight else ""
    parts.append(f"l_text:{font}_{size}{fw}:{t(s)},co_rgb:{color}")
    return ",".join(parts)+f"/fl_layer_apply,g_{g},x_{x},y_{y}"
def rect(color,w,h,x,y):
    return f"l_sample,w_{w},h_{h},c_scale,e_colorize:100,co_rgb:{color}/fl_layer_apply,g_north_west,x_{x},y_{y}"
def card(tag, de, ru, ex, exru, note):
    L=["w_1080,h_1080,c_fill,e_colorize:100,co_rgb:0f1220",
       rect("111111",360,14,0,0), rect("dd0000",360,14,360,0), rect("ffce00",360,14,720,0),
       text(tag,"Montserrat",30,"bold","ffce00",90,90),
       text(de,"Montserrat",96,"bold","f4f1ea",90,170,w=900),
       text(ru,"Montserrat",44,"bold","ffce00",90,520,w=900),
       rect("dd0000",6,120,90,640),
       text(ex,"Montserrat",36,"bold","f4f1ea",125,648,w=860),
       text(exru,"Montserrat",30,None,"a9adc0",125,710,w=860),
       text(note,"Montserrat",26,None,"a9adc0",90,960),
       text("@lingofydeutsch","Montserrat",30,"bold","f4f1ea",90,955,g="north_east")]
    return f"https://res.cloudinary.com/{CLOUD}/image/upload/"+"/".join(L)+"/sample.jpg"
if __name__=="__main__":
    a=json.loads(sys.argv[1]); print(card(**a))
