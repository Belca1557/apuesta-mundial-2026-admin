#!/usr/bin/env python3
"""Lee la API de football-data.org y escribe resultados.json.
Mapea cada partido por el par de codigos de 3 letras (unico en fase de grupos).
Requiere variable de entorno FOOTBALL_TOKEN (token gratis de football-data.org)."""
import os, json, sys, urllib.request

TOKEN = os.environ.get("FOOTBALL_TOKEN", "").strip()
BASE  = "https://api.football-data.org/v4/competitions/WC"
HDR   = {"X-Auth-Token": TOKEN}

# Alias por si la API usa un codigo distinto al de la quiniela (codigo_quiniela: [codigos_api...])
ALIAS = {
    "RSA":["RSA","ZAF"], "KOR":["KOR","COR"], "CUW":["CUW","CUR"],
    "COD":["COD","CGO","DRC"], "CPV":["CPV","CAP"], "BIH":["BIH","BOS"],
}
def norm(code):
    code=(code or "").upper()
    for k,al in ALIAS.items():
        if code in al: return k
    return code

def get(url):
    req=urllib.request.Request(url, headers=HDR)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

def main():
    if not TOKEN:
        print("ERROR: falta FOOTBALL_TOKEN"); sys.exit(1)
    fixtures=json.load(open("fixtures.json"))
    # par de codigos -> (mid, local_quiniela)
    pair2mid={}
    for mid,(loc,vis) in fixtures.items():
        pair2mid[frozenset([loc,vis])]=(mid,loc)

    out={"updated":None,"matches":{},"scorers":[]}
    # --- partidos ---
    data=get(f"{BASE}/matches")
    out["updated"]=data.get("filters",{}).get("season") and None
    import datetime as dt
    out["updated"]=dt.datetime.utcnow().replace(microsecond=0).isoformat()+"Z"
    for m in data.get("matches",[]):
        h=norm(m.get("homeTeam",{}).get("tla")); a=norm(m.get("awayTeam",{}).get("tla"))
        key=frozenset([h,a])
        if key not in pair2mid:  # solo nos interesan los 72 de grupos
            continue
        mid,loc=pair2mid[key]
        st=m.get("status")
        ft=m.get("score",{}).get("fullTime",{})
        hg,ag=ft.get("home"),ft.get("away")
        rec={"st":st}
        if hg is not None and ag is not None:
            # orientar al local de la quiniela
            if h==norm(loc): rec["rl"],rec["rv"]=hg,ag
            else:            rec["rl"],rec["rv"]=ag,hg
        mn=m.get("minute")
        if mn and st in ("IN_PLAY","PAUSED"): rec["min"]=f"{mn}'"
        out["matches"][mid]=rec

    # --- goleadores (top 3) ---
    try:
        sc=get(f"{BASE}/scorers?limit=10")
        for s in sc.get("scorers",[])[:3]:
            out["scorers"].append({"n":s.get("player",{}).get("name"),
                                   "t":(s.get("team",{}) or {}).get("tla"),
                                   "g":s.get("goals")})
    except Exception as e:
        print("scorers no disponible:",e)

    json.dump(out, open("resultados.json","w"), ensure_ascii=False, indent=0)
    fin=sum(1 for v in out["matches"].values() if v.get("st") in ("FINISHED","AWARDED"))
    liv=sum(1 for v in out["matches"].values() if v.get("st") in ("IN_PLAY","PAUSED"))
    print(f"OK · {len(out['matches'])} partidos mapeados · {fin} finalizados · {liv} en vivo · {len(out['scorers'])} goleadores")

if __name__=="__main__":
    main()
