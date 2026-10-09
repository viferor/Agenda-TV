"""Genera datos.json para la Agenda TV a partir de la guía XMLTV pública de dobleM."""
import xml.etree.ElementTree as ET, re, json, sys, datetime as dt, urllib.request, gzip, io

SRC = "https://raw.githubusercontent.com/davidmuma/EPG_dobleM/master/guiatv.xml"
TVE = [  # TDT nacional sin canales infantiles, en orden aproximado del mando + Canal Sur
    ("La 1 HD","La 1"),("La 2","La 2"),("Antena 3 HD","Antena 3"),("Cuatro HD","Cuatro"),("Telecinco HD","Telecinco"),
    ("La Sexta HD","laSexta"),("Canal Sur HD","Canal Sur"),("24 Horas","24h"),("Teledeporte","Teledeporte"),
    ("Neox","Neox"),("Nova","Nova"),("Mega","Mega"),("Atreseries","Atreseries"),
    ("Factoría de Ficción","FDF"),("Energy","Energy"),("Divinity","Divinity"),("Be Mad","Be Mad"),
    ("Ten","Ten"),("DMAX","DMAX"),("DKISS","DKISS"),("TRECE","TRECE"),("Real Madrid TV","Real Madrid TV"),
    ("El Toro TV","El Toro TV"),("Squirrel TV","Squirrel"),("Veo7","Veo7"),
]

# canal EPG -> (nombre visible, app oficial, web)
APPS = [
    (r"^M\+ |^Movistar Plus|^Vamos BAR", "Movistar Plus+", "https://www.movistarplus.es"),
    (r"^DAZN", "DAZN", "https://www.dazn.com/es-ES"),
    (r"^LaLiga TV", "LaLiga TV Hypermotion", "https://www.laliga.com/laliga-tv"),
    (r"^(La 1|La 2|Teledeporte|24 Horas|Clan)", "RTVE Play", "https://www.rtve.es/play/"),
    (r"^(Antena 3|La Sexta|Neox|Nova|Mega|Atreseries)", "Atresplayer", "https://www.atresplayer.com/directos/"),
    (r"^(Cuatro|Telecinco|Factoría de Ficción|Energy|Divinity|Be Mad)", "Mediaset Infinity", "https://www.mitele.es/directo/"),
    (r"^(Canal Sur|Andalucía TV)", "Canal Sur Más", "https://www.canalsur.es/"),
    (r"^TRECE", "TRECE", "https://www.trecetv.es"),
    (r"^Real Madrid TV", "Real Madrid TV", "https://www.realmadrid.com"),
    (r"^Eurosport", "Eurosport / HBO Max", "https://www.eurosport.es"),
    (r"^etb", "EITB", "https://www.eitb.eus/es/"),
    (r"^(TV3|Esport 3|SX3|3Cat)", "3Cat", "https://www.3cat.cat"),
    (r"^Primera Federaci", "Movistar Plus+", "https://www.movistarplus.es"),
]
def app_for(ch):
    for rx, name, url in APPS:
        if re.search(rx, ch): return name, url
    return ch, ""

def nice_channel(ch):
    ch = re.sub(r" HD$", "", ch)
    return ch.replace("M+ ", "M+ ")

def ts(s):  # '20261009075000 +0200'
    d = dt.datetime.strptime(s, "%Y%m%d%H%M%S %z")
    return d.isoformat()

def cats(desc):
    m = re.match(r"\s*([^|]*?)\s*\|", desc or "")
    return m.group(1).split(",") if m else []

def classify(title, c):
    # DIRECTO = emisión en directo confirmada; "TBC ..." = franja de directo de Movistar Plus+
    # cuyos partidos aún no se han anunciado (pasa en torneos de tenis los días siguientes)
    if not (title.startswith("DIRECTO") or title.startswith("TBC ")): return None
    if "Programa deportes" in c or "Programa Deportivo" in c: return None
    if "Fútbol" in c and re.search(r"LALIGA (EA SPORTS|HYPERMOTION)", title): return "laliga"
    if "Fútbol" in c and "UEFA Champions League" in title: return "champions"
    if "Ciclismo" in c: return "ciclismo"
    t = re.sub(r"^DIRECTO\s*", "", title)
    if re.match(r"(Previo|Post|El Post)\b", t): pass
    elif re.search(r"· Mundial F1\b", title): return "motor"
    elif re.search(r"· MotoGP\b", title): return "motor"
    if "Tenis" in c: return "tenis"
    return None

def parse_title(title):
    t = re.sub(r"^DIRECTO\s*", "", title)
    left, _, comp = t.partition(" · ")
    left = re.sub(r"\s*T\d{2}/\d{2}$|\s*T\d{4}$", "", left).strip()
    rnd, ev = "", left
    m = re.match(r"^(.+?):\s*(.+)$", left)
    if m: rnd, ev = m.group(1), m.group(2)
    if ev.startswith("TBC") or not ev: ev = "Partidos por confirmar"
    vo = "(VO)" in ev
    ev = ev.replace("(VO)", "").strip()
    comp = comp.strip() or left
    if comp == left and rnd == "": ev = left
    return ev, rnd, comp, vo

def main(path):
    root = ET.parse(path).getroot()
    gen = root.get("generator-info-name", "")
    events = {}
    tve = {k: [] for k, _ in TVE}
    for p in root.iter("programme"):
        ch = p.get("channel"); title = p.findtext("title") or ""; desc = p.findtext("desc") or ""
        start, stop = ts(p.get("start")), ts(p.get("stop"))
        if ch in tve:
            d = re.sub(r"^\s*[^·]*·\s*", "", desc, count=1) if "|" in desc.split("·")[0] else desc
            tve[ch].append({"t": title, "s": start, "e": stop, "g": ",".join(cats(desc)[:2]), "d": d.split("\n·")[0].strip()[:300]})
        sport = classify(title, cats(desc))
        if not sport: continue
        ev, rnd, comp, vo = parse_title(title)
        key = (sport, start[:16], ev.lower())
        e = events.setdefault(key, {"sport": sport, "s": start, "e": stop, "ev": ev, "rnd": rnd, "comp": comp, "ch": [],
                                    "tbc": ev == "Partidos por confirmar"})
        if "BAR" in ch: continue  # canales para hostelería
        name, url = app_for(ch)
        e["ch"].append({"c": nice_channel(ch), "app": name, "url": url, "vo": vo})
    out_ev = sorted(events.values(), key=lambda x: (x["s"], x["ev"]))
    for e in out_ev:
        e["ch"].sort(key=lambda c: (c["vo"], c["c"]))
    tv = [{"id": k, "name": n, "app": app_for(k)[0], "url": app_for(k)[1], "p": sorted(tve[k], key=lambda x: x["s"])} for k, n in TVE]
    json.dump({"generado": dt.datetime.now(dt.timezone.utc).isoformat(), "fuente": gen, "eventos": out_ev, "tve": tv},
              open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print(len(out_ev), "eventos;", {t["id"]: len(t["p"]) for t in tv})

if __name__ == "__main__":
    # Uso: python3 build.py [guia.xml|--descargar] [salida.json]
    src = sys.argv[1] if len(sys.argv) > 1 else "--descargar"
    if len(sys.argv) < 3: sys.argv[2:] = ["datos.json"]
    if src == "--descargar":
        tmp = "guiatv.xml"
        urllib.request.urlretrieve(SRC, tmp)
        src = tmp
    main(src)
