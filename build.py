"""Genera datos.json (agenda deportiva y parrilla de la TDT) y datos-mplus.json (parrilla de
Movistar Plus+) para la Agenda TV a partir de la guía XMLTV pública de dobleM."""
import xml.etree.ElementTree as ET, re, json, sys, datetime as dt, urllib.request, gzip, io

SRC = "https://raw.githubusercontent.com/davidmuma/EPG_dobleM/master/guiatv.xml"
TVE = [  # TDT nacional sin canales infantiles, en orden aproximado del mando + Canal Sur
    ("La 1 HD","La 1"),("La 2","La 2"),("Antena 3 HD","Antena 3"),("Cuatro HD","Cuatro"),("Telecinco HD","Telecinco"),
    ("La Sexta HD","laSexta"),("Canal Sur HD","Canal Sur"),("24 Horas","24h"),("Teledeporte","Teledeporte"),
    ("Neox","Neox"),("Nova","Nova"),("Mega","Mega"),("Atreseries","Atreseries"),
    ("Factoría de Ficción","FDF"),("Energy","Energy"),("Divinity","Divinity"),("Be Mad","Be Mad"),
    ("Ten","Ten"),("DMAX","DMAX"),("DKISS","DKISS"),("TRECE","TRECE"),("Real Madrid TV","Real Madrid TV"),
    ("El Toro TV","El Toro TV"),("Squirrel TV","Squirrel"),("Veo7","Veo7"),
    ("Replay","Replay"),("DBike","DBike"),
]
MOVISTAR = [  # parrilla de Movistar Plus+, en el orden del dial de la plataforma
    ('M+ Estrenos HD', 'M+ Estrenos'), ('M+ Hits HD', 'M+ Hits'), ('M+ Originales HD', 'M+ Originales'),
    ('M+ Terror', 'M+ Terror'), ('M+ Documentales HD', 'M+ Documentales'), ('M+ Romance', 'M+ Romance'),
    ('M+ Clásicos HD', 'M+ Clásicos'), ('M+ Acción HD', 'M+ Acción'), ('M+ Comedia HD', 'M+ Comedia'),
    ('M+ Drama HD', 'M+ Drama'), ('M+ Indie HD', 'M+ Indie'), ('M+ Cine Español', 'M+ Cine Español'),
    ('M+ PopUp', 'M+ PopUp'), ('M+ PopUp 2', 'M+ PopUp 2'), ('Canal FlixOlé 1', 'Canal FlixOlé 1'),
    ('Canal FlixOlé 2', 'Canal FlixOlé 2'), ('TCM HD', 'TCM'), ('BBC Series', 'BBC Series'),
    ('BBC Earth', 'BBC Earth'), ('BBC Top Gear', 'BBC Top Gear'), ('BBC Lifestyle', 'BBC Lifestyle'),
    ('STAR Channel HD', 'STAR Channel'), ('AXN HD', 'AXN'), ('Warner TV HD', 'Warner TV'),
    ('Comedy Central HD', 'Comedy Central'), ('Calle 13 HD', 'Calle 13'), ('Cosmo HD', 'Cosmo'),
    ('SciFi HD', 'SciFi'),
    # documentales, ocio e infantiles
    ('Caza y Pesca HD', 'Caza y Pesca'), ('Iberalia TV', 'Iberalia TV'), ('National Geographic HD', 'National Geographic'),
    ('Nat Geo Wild HD', 'Nat Geo Wild'), ('BBC History', 'BBC History'), ('Discovery', 'Discovery'),
    ('BBC Food', 'BBC Food'), ('Baby TV', 'Baby TV'), ('Disney Channel', 'Disney Channel'),
    ('Nick JR', 'Nick JR'), ('Nickelodeon HD', 'Nickelodeon'), ('Dreamworks HD', 'Dreamworks'),
    ('Boing', 'Boing'), ('Clan', 'Clan'), ('MTV España', 'MTV España'),
    ('Mezzo', 'Mezzo'), ('Mezzo Live HD', 'Mezzo Live'), ('Classica HD', 'Classica'),
    ('M+ Cero', 'M+ Cero'),
    # noticias e internacional
    ('BBC World News Europe HD', 'BBC World News Europe'), ('CNN International Europe', 'CNN International Europe'), ('Al Jazeera English HD', 'Al Jazeera English'),
    ('France 24 (en Francais)', 'France 24 (en Francais)'), ('CNBC Europe HD', 'CNBC Europe'), ('TV5 Monde Europe HD', 'TV5 Monde Europe'),
    ('Bloomberg TV Europe', 'Bloomberg TV Europe'), ('Cubavisión Internacional HD', 'Cubavisión Internacional'), ('Telesur HD', 'Telesur'),
    # autonómicas y locales
    ('Canal Sur Andalucía', 'Canal Sur Andalucía'), ('TVG Europa HD', 'TVG Europa'), ('Canal Extremadura SAT', 'Canal Extremadura SAT'),
    ('Aragón TV Internacional', 'Aragón TV Internacional'), ('À Punt', 'À Punt'), ('Aragón TV', 'Aragón TV'),
    ('Navarra TV', 'Navarra TV'), ('Navarra TV 2', 'Navarra TV 2'), ('TPA7 Asturias', 'TPA7 Asturias'),
    ('TPA8 Asturias', 'TPA8 Asturias'), ('CMM TV', 'CMM TV'), ('La 7 CyL', 'La 7 CyL'),
    ('etb1', 'etb1'), ('etb2', 'etb2'), ('TVG', 'TVG'),
    ('TVG2', 'TVG2'), ('Canal Extremadura', 'Canal Extremadura'), ('Telemadrid', 'Telemadrid'),
    ('La Otra', 'La Otra'), ('TV3', 'TV3'), ('La 7 Murcia', 'La 7 Murcia'),
    ('Andalucía TV', 'Andalucía TV'), ('La Ocho Mediterráneo', 'La Ocho Mediterráneo'), ('IB3 TV Illes Balears', 'IB3 TV Illes Balears'),
    ('TV Canaria', 'TV Canaria'), ('Atlántico TV', 'Atlántico TV'), ('Canal RED', 'Canal RED'),
    # otros canales del dial
    ('HBO Max Avances', 'HBO Max Avances'), ('SkyShowtime', 'SkyShowtime'), ('AXN Movies HD', 'AXN Movies'),
    ('etb1ON', 'etb1ON'), ('etb2ON', 'etb2ON'), ('EuroNews', 'EuroNews'),
    ('Negocios TV', 'Negocios TV'), ('CGTN Español', 'CGTN Español'), ('CGTN Documentary', 'CGTN Documentary'),
    ('UCL', 'UCL'), ('Canal de las Estrellas', 'Canal de las Estrellas'), ('TV Chile', 'TV Chile'),
    ('Nuestra Tele Internacional', 'Nuestra Tele Internacional'), ('EWTN', 'EWTN'), ('Telemadrid Internacional', 'Telemadrid Internacional'),
    ('SX3', 'SX3'), ('Esport 3', 'Esport 3'), ('3CatInfo', '3CatInfo'),
    ('Betevé', 'Betevé'),
    # deportes: canales propios y de terceros del dial (DAZN, LaLiga TV, Eurosport…)
    ('Movistar Plus HD', 'Movistar Plus'), ('Primera Federación', 'Primera Federación'), ('M+ Vamos HD', 'M+ Vamos'),
    ('M+ LaLiga HD', 'M+ LaLiga'), ('DAZN LaLiga HD', 'DAZN LaLiga'), ('LaLiga TV Hypermotion HD', 'LaLiga TV Hypermotion'),
    ('M+ LaLiga 2 HD', 'M+ LaLiga 2'), ('DAZN LaLiga 2 HD', 'DAZN LaLiga 2'), ('LaLiga TV Hypermotion 2', 'LaLiga TV Hypermotion 2'),
    ('M+ Liga de Campeones HD', 'M+ Liga de Campeones'), ('M+ Liga de Campeones 2 HD', 'M+ Liga de Campeones 2'), ('M+ Liga de Campeones 3 HD', 'M+ Liga de Campeones 3'),
    ('M+ Deportes HD', 'M+ Deportes'), ('M+ Deportes 2 HD', 'M+ Deportes 2'), ('M+ Deportes 3', 'M+ Deportes 3'),
    ('M+ Baloncesto', 'M+ Baloncesto'), ('M+ Baloncesto 2', 'M+ Baloncesto 2'), ('M+ Baloncesto 3', 'M+ Baloncesto 3'),
    ('M+ Baloncesto 4', 'M+ Baloncesto 4'), ('M+ Baloncesto 5', 'M+ Baloncesto 5'), ('M+ Golf HD', 'M+ Golf'),
    ('M+ Golf 2 HD', 'M+ Golf 2'), ('DAZN F1 HD', 'DAZN F1'), ('DAZN MotoGP', 'DAZN MotoGP'),
    ('DAZN 1 HD', 'DAZN 1'), ('DAZN 2 HD', 'DAZN 2'), ('DAZN Baloncesto', 'DAZN Baloncesto'),
    ('DAZN Baloncesto 2', 'DAZN Baloncesto 2'), ('DAZN Baloncesto 3', 'DAZN Baloncesto 3'), ('Eurosport 1 HD', 'Eurosport 1'),
    ('Eurosport 2', 'Eurosport 2'),
    # multievento, feeds numerados y versiones HDR/UHD (casi todos emiten solo algunos días)
    ('M+ Liga de Campeones 4', 'M+ Liga de Campeones 4'), ('M+ Liga de Campeones 5', 'M+ Liga de Campeones 5'), ('M+ Liga de Campeones 6', 'M+ Liga de Campeones 6'),
    ('M+ Liga de Campeones 7', 'M+ Liga de Campeones 7'), ('M+ Liga de Campeones 8', 'M+ Liga de Campeones 8'), ('M+ Liga de Campeones 9', 'M+ Liga de Campeones 9'),
    ('M+ Liga de Campeones 10', 'M+ Liga de Campeones 10'), ('M+ Liga de Campeones 11', 'M+ Liga de Campeones 11'), ('M+ Liga de Campeones 12', 'M+ Liga de Campeones 12'),
    ('M+ Liga de Campeones 13', 'M+ Liga de Campeones 13'), ('M+ LaLiga 3 HD', 'M+ LaLiga 3'), ('M+ LaLiga 4', 'M+ LaLiga 4'),
    ('M+ LaLiga 5', 'M+ LaLiga 5'), ('M+ LaLiga 6', 'M+ LaLiga 6'), ('DAZN LaLiga 3', 'DAZN LaLiga 3'),
    ('DAZN LaLiga 4', 'DAZN LaLiga 4'), ('DAZN LaLiga 5', 'DAZN LaLiga 5'), ('DAZN LaLiga 6', 'DAZN LaLiga 6'),
    ('M+ Vamos 2', 'M+ Vamos 2'), ('M+ Vamos 3', 'M+ Vamos 3'), ('LaLiga TV Hypermotion 3', 'LaLiga TV Hypermotion 3'),
    ('LaLiga TV Hypermotion 4', 'LaLiga TV Hypermotion 4'), ('M+ Deportes 4', 'M+ Deportes 4'), ('M+ Deportes 5', 'M+ Deportes 5'),
    ('M+ Deportes 6', 'M+ Deportes 6'), ('M+ Deportes 7', 'M+ Deportes 7'), ('M+ Deportes 8', 'M+ Deportes 8'),
    ('DAZN 3 HD', 'DAZN 3'), ('DAZN 4 HD', 'DAZN 4'), ('M+ LaLiga HDR', 'M+ LaLiga HDR'),
    ('M+ LaLiga 2 HDR', 'M+ LaLiga 2 HDR'), ('M+ Liga de Campeones HDR', 'M+ Liga de Campeones HDR'),
    ('M+ Liga de Campeones 2 HDR', 'M+ Liga de Campeones 2 HDR'), ('Eurosport 4K', 'Eurosport 4K'),
    ('M+ Wimbledon UHD', 'M+ Wimbledon'),
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
    (r"^Replay$", "Replay (web gratuita)", "https://www.replaytv.es/en-directo"),
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

# Categoría de contenido de cada canal, para los filtros de la parrilla. Primero se miran las
# familias conocidas (las de la lista anterior son las que la guía no siempre etiqueta) y, si no
# encaja ninguna, se toma el género que más minutos ocupa en la semana.
CAT_GENRE = {"Cine": "cine", "Cortometrajes": "cine", "Series": "series", "Deportes": "deportes",
             "Documentales": "docs", "Infantil": "infantil", "Información": "noticias", "Música": "musica"}
CAT_ORDER = ["cine", "series", "deportes", "docs", "infantil", "noticias", "musica", "otros"]
CAT_RULES = [
    (r"^(M\+ (LaLiga|Liga de Campeones|Deportes|Vamos|Baloncesto|Golf|Wimbledon)|DAZN|Eurosport|LaLiga TV|Primera Federaci|Teledeporte|Real Madrid TV|Esport 3|Replay)", "deportes"),
    (r"^(Baby TV|Disney Channel|Nick JR|Nickelodeon|Dreamworks|Boing|Clan|SX3|Pocoyó|Lolly Kids)", "infantil"),
    (r"^(M\+ (Estrenos|Hits|Acción|Comedia|Drama|Clásicos|Cine Español|Indie|Romance|Terror|PopUp)|Canal FlixOlé|TCM|AXN Movies|BOM Cine|Cine Feel Good|Cines Verdi|Be Mad)", "cine"),
    (r"^(M\+ Originales|BBC Series|STAR Channel|AXN|Warner TV|Comedy Central|Calle 13|Cosmo|SciFi|Sundance TV|SkyShowtime|AMC)", "series"),
    (r"^(M\+ Documentales|BBC (Earth|History|Food|Lifestyle|Top Gear)|National Geographic|Nat Geo Wild|Discovery|Historia|Odisea|Caza y Pesca|Iberalia|NatureTime)", "docs"),
    (r"^(24 Horas|BBC World|CNN|Al Jazeera|France 24|CNBC|Bloomberg|EuroNews|Negocios TV|CGTN|Telesur|Cubavisión|EWTN|TV5 Monde|3CatInfo)", "noticias"),
    (r"^(Mezzo|Classica|MTV|Sol Música|Qello|Qwest|TRACE)", "musica"),
]
def channel_cat(ch, minutes):
    for rx, cat in CAT_RULES:
        if re.search(rx, ch): return cat
    best, bv = "", 0
    for cat in CAT_ORDER:  # el orden hace de desempate
        v = minutes.get(cat, 0)
        if v > bv: bv, best = v, cat
    return best or "otros"

def ts_dt(s):  # '20261009075000 +0200'
    return dt.datetime.strptime(s, "%Y%m%d%H%M%S %z")

def ts(s):
    return ts_dt(s).isoformat()

def cats(desc):
    m = re.match(r"\s*([^|]*?)\s*\|", desc or "")
    return m.group(1).split(",") if m else []

CREDITOS = ("País", "Dirección", "Presentación", "Presentador", "Presentadores", "Reparto", "Guion", "Música")

def ficha(title, start, stop, desc):
    """Programa de la parrilla con su ficha: género, año, edad, nota, sinopsis y créditos."""
    p = {"t": title, "s": start, "e": stop}
    lines = [l.strip() for l in (desc or "").split("\n")]
    head = lines[0] if lines else ""
    syn, extra = [], {}
    if "|" in head.split("·")[0]:
        meta, _, rest = head.partition("·")
        parts = [x.strip() for x in meta.split("|") if x.strip()]
        if parts and not re.match(r"^\d{4}$|^\+?\d+$|^TP$|^\*", parts[0]):
            p["g"] = parts.pop(0).replace(",", " · ")
        for x in parts:
            if re.fullmatch(r"\d{4}", x): p["y"] = x
            elif re.fullmatch(r"TP|\+\d+", x): p["a"] = x
            elif x.startswith("*"): p["r"] = x.lstrip("*").replace("/10", "")
        if rest.strip(): syn.append(rest.strip())
    else:
        syn.append(head.lstrip("· ").strip())
    for l in lines[1:]:
        l = l.lstrip("·").strip()
        m = re.match(r"^([A-ZÁÉÍÓÚ][\wáéíóúñ ]{1,20}):\s*(.+)$", l)
        if m and m.group(1) in CREDITOS:
            extra[m.group(1)] = m.group(2).rstrip(".")[:220]
        elif m:
            continue  # productora, producción, etc.
        elif l:
            syn.append(l)
    s = " ".join(syn).strip()
    if s and s not in ("Sin detalles...", "Programa por determinar..."):
        p["d"] = s[:700]
    if extra: p["c"] = extra
    # serie: "Título T4 E83 · Nombre del episodio"
    base, _, ep = title.partition(" · ")
    m = re.match(r"^(.*?)\s+T(\d+)(?:\s+E(\d+))?$", base)
    if m:
        p["sn"] = m.group(1); p["se"] = m.group(2)
        if m.group(3): p["ep"] = m.group(3)
        if ep: p["et"] = ep
    return p

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
    mp = {k: [] for k, _ in MOVISTAR}
    catmin = {}  # canal -> {categoría: minutos en la semana}, para los filtros de contenido
    for p in root.iter("programme"):
        ch = p.get("channel"); title = p.findtext("title") or ""; desc = p.findtext("desc") or ""
        d0, d1 = ts_dt(p.get("start")), ts_dt(p.get("stop"))
        start, stop = d0.isoformat(), d1.isoformat()
        if ch in tve or ch in mp:
            genre = (cats(desc) or [""])[0].strip()
            if genre:  # las franjas de relleno de la guía vienen sin género y no dicen nada del canal
                cat = CAT_GENRE.get(genre, "otros")
                acc = catmin.setdefault(ch, {})
                acc[cat] = acc.get(cat, 0) + (d1 - d0).total_seconds() / 60
        if ch in tve:
            tve[ch].append(ficha(title, start, stop, desc))
        elif ch in mp:  # parrilla de Movistar Plus+
            mp[ch].append(ficha(title, start, stop, desc))
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
    tv = [{"id": k, "name": n, "app": app_for(k)[0], "url": app_for(k)[1], "cat": channel_cat(k, catmin.get(k, {})),
           "p": sorted(tve[k], key=lambda x: x["s"])} for k, n in TVE]
    # La 1 HD tiene que seguir siendo el primer canal de "tve": la página lo usa para saber qué días hay parrilla
    mplus = [{"id": k, "name": n, "app": app_for(k)[0], "url": app_for(k)[1], "cat": channel_cat(k, catmin.get(k, {})),
              "p": sorted(mp[k], key=lambda x: x["s"])} for k, n in MOVISTAR]
    mplus = [c for c in mplus if c["p"]]  # si la guía no trae programación de un canal, no se publica una fila vacía
    gen_iso = dt.datetime.now(dt.timezone.utc).isoformat()
    out = sys.argv[2]
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"generado": gen_iso, "fuente": gen, "eventos": out_ev, "tve": tv},
                  f, ensure_ascii=False, separators=(",", ":"))
    # El dial de Movistar Plus+ son ~150 canales con siete días de programación: va en su propio
    # archivo (datos-mplus.json) y la página lo descarga solo al abrir esa pestaña.
    mp_out = re.sub(r"\.json$", "", out) + "-mplus.json"
    with open(mp_out, "w", encoding="utf-8") as f:
        json.dump({"generado": gen_iso, "fuente": gen, "mplus": mplus}, f, ensure_ascii=False, separators=(",", ":"))
    print(len(out_ev), "eventos;", {t["id"]: len(t["p"]) for t in tv})
    print(mp_out + ":", len(mplus), "canales de Movistar Plus+")

if __name__ == "__main__":
    # Uso: python3 build.py [guia.xml|--descargar] [salida.json]
    src = sys.argv[1] if len(sys.argv) > 1 else "--descargar"
    if len(sys.argv) < 3: sys.argv[2:] = ["datos.json"]
    if src == "--descargar":
        tmp = "guiatv.xml"
        urllib.request.urlretrieve(SRC, tmp)
        src = tmp
    main(src)
