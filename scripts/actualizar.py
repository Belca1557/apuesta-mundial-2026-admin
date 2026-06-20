#!/usr/bin/env python3
"""Lee football-data.org y ACTUALIZA resultados.json SOLO si cambio algo real.
- Fusiona (respeta ediciones manuales), reconoce siglas (SAU=KSA, etc.).
- No reescribe si matches/scorers no cambiaron -> sin commits ni rebuilds inutiles.
Requiere FOOTBALL_TOKEN."""
import os, json, sys, datetime as dt, urllib.request
TOKEN = os.environ.get("FOOTBALL_TOKEN", "").strip()
BASE  = "https://api.football-data.org/v4/competitions/WC"
HDR   = {"X-Auth-Token": TOKEN}
ALIAS = {
    "KSA":["KSA","SAU"], "KOR":["KOR","COR","PRK"], "RSA":["RSA","ZAF","RZA"],
    "CIV":["CIV","IVO"], "CUW":["CUW","CUR"], "COD":["COD","CGO","DRC","ZAI"],
    "CPV":["CPV","CAP"], "BIH":["BIH","BOS"], "URU":["URU","URG"], "IRN":["IRN","IRA"],
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
    pair2mid={ frozenset([norm(loc),norm(vis)]):(mid,loc) for mid,(loc,vis) in fixtures.items() }
    try:
        prev=json.load(open("resultados.json"))
        if not isinstance(prev,dict): prev={}
    except Exception:
        prev={}
    prev_matches=dict(prev.get("matches",{}))
    prev_scorers=list(prev.get("scorers",[]))

    matches=dict(prev_matches)   # parte de lo previo (preserva manual)
    data=get(f"{BASE}/matches")
    mapped=0
    for m in data.get("matches",[]):
        h=norm(m.get("homeTeam",{}).get("tla")); a=norm(m.get("awayTeam",{}).get("tla"))
        key=frozenset([h,a])
        if key not in pair2mid: continue
        mid,loc=pair2mid[key]
        st=m.get("status"); ft=m.get("score",{}).get("fullTime",{}) or {}
        hg,ag=ft.get("home"),ft.get("away")
        rec={"st":st}
        if hg is not None and ag is not None:
            if h==norm(loc): rec["rl"],rec["rv"]=hg,ag
            else:            rec["rl"],rec["rv"]=ag,hg
        matches[mid]=rec   # sin campo 'min' -> no commitea por el reloj
        mapped+=1

    scorers=prev_scorers
    try:
        sc=get(f"{BASE}/scorers?limit=10")
        top=[{"n":s.get("player",{}).get("name"),"t":(s.get("team",{}) or {}).get("tla"),"g":s.get("goals")} for s in sc.get("scorers",[])[:3]]
        if top: scorers=top
    except Exception as e:
        print("scorers no disponible:",e)

    # SOLO escribir si cambio algo real (ignora el timestamp)
    if matches==prev_matches and scorers==prev_scorers and prev:
        print(f"Sin cambios reales ({mapped} mapeados). No se reescribe.")
        return
    out={"updated":dt.datetime.utcnow().replace(microsecond=0).isoformat()+"Z",
         "matches":matches, "scorers":scorers}
    json.dump(out, open("resultados.json","w"), ensure_ascii=False, indent=0)
    fin=sum(1 for v in matches.values() if v.get("st") in ("FINISHED","AWARDED"))
    liv=sum(1 for v in matches.values() if v.get("st") in ("IN_PLAY","PAUSED"))
    print(f"CAMBIOS detectados · {mapped} mapeados · {fin} finalizados · {liv} en vivo · archivo actualizado")
if __name__=="__main__":
    main()
