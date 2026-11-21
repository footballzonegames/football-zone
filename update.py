"""Descarga resultados, próximos partidos y clasificaciones de football-data.org
y los guarda en data.json. Solo usa la librería estándar de Python."""
import difflib, json, os, sys, time, unicodedata, urllib.request
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

KEY = os.environ.get("FOOTBALL_DATA_KEY", "").strip()
if not KEY:
    sys.exit("Falta la clave FOOTBALL_DATA_KEY")

BASE = "https://api.football-data.org/v4"
LIGAS = {"laliga": "PD", "premier": "PL", "seriea": "SA", "bundes": "BL1",
         "ligue1": "FL1", "portugal": "PPL", "ered": "DED", "champ": "CL"}
DIAS = ["lun", "mar", "mié", "jue", "vie", "sáb", "dom"]
MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
MAD = ZoneInfo("Europe/Madrid")


TEAMS = {"laliga": ["Barcelona", "Real Madrid", "Atlético", "Betis", "R. Sociedad", "Sevilla", "Athletic", "Villarreal", "Deportivo", "Racing", "Celta", "Alavés", "Espanyol", "Rayo", "Getafe", "Osasuna", "Levante", "Elche", "Valencia", "Málaga"], "premier": ["Arsenal", "Brighton", "Man. City", "Liverpool", "Chelsea", "Everton", "Bournemouth", "Brentford", "Leeds", "Aston Villa", "Tottenham", "Newcastle", "Hull", "Ipswich", "Fulham", "Nott. Forest", "Coventry", "Man. United", "Sunderland", "Crystal Palace"], "seriea": ["Lazio", "Inter", "Roma", "Milan", "Como", "Frosinone", "Juventus", "Bologna", "Cagliari", "Napoli", "Torino", "Atalanta", "Genoa", "Lecce", "Fiorentina", "Parma", "Sassuolo", "Monza", "Venezia", "Udinese"], "bundes": ["Bayern", "Dortmund", "Friburgo", "Leipzig", "Leverkusen", "Bremen", "Elversberg", "Stuttgart", "Hoffenheim", "Frankfurt", "Hamburgo", "Mainz", "Paderborn", "Augsburg", "Colonia", "Union Berlín", "Schalke", "Gladbach"], "ligue1": ["PSG", "Lille", "Paris FC", "Marsella", "Lyon", "Niza", "Mónaco", "Rennes", "Brest", "Lorient", "Lens", "Toulouse", "Estrasburgo", "Auxerre", "Le Mans", "Angers", "Troyes", "Le Havre"], "portugal": ["FC Porto", "Benfica", "Sporting CP", "Santa Clara", "Arouca", "Académico Viseu", "Gil Vicente", "Braga", "Moreirense", "Famalicão", "Alverca", "Estrela Amadora", "Nacional", "Vitória SC"], "ered": ["PSV", "Feyenoord", "Ajax", "Twente", "AZ", "Heerenveen", "Fortuna Sittard", "Go Ahead Eagles", "Groningen", "Cambuur", "NEC", "Sparta Rotterdam", "Zwolle", "Utrecht", "Excelsior", "Telstar", "ADO Den Haag", "Willem II"], "champ": ["ADO Den Haag", "AEK Atenas", "AZ", "Académico Viseu", "Ajax", "Alavés", "Alverca", "Angers", "Arouca", "Arsenal", "Aston Villa", "Atalanta", "Athletic", "Atlético", "Augsburg", "Auxerre", "Barcelona", "Bayern", "Benfica", "Betis", "Bodø/Glimt", "Bologna", "Bournemouth", "Braga", "Bremen", "Brentford", "Brest", "Brighton", "Brujas", "Cagliari", "Cambuur", "Celta", "Chelsea", "Colonia", "Como", "Coventry", "Crystal Palace", "Deportivo", "Dortmund", "Elche", "Elversberg", "Espanyol", "Estrasburgo", "Estrela Amadora", "Everton", "Excelsior", "FC Porto", "Famalicão", "Fenerbahçe", "Feyenoord", "Fiorentina", "Fortuna Sittard", "Frankfurt", "Friburgo", "Frosinone", "Fulham", "Galatasaray", "Genoa", "Getafe", "Gil Vicente", "Gladbach", "Go Ahead Eagles", "Groningen", "Hamburgo", "Heerenveen", "Hoffenheim", "Hull", "Inter", "Ipswich", "Juventus", "LASK", "Lazio", "Le Havre", "Le Mans", "Lecce", "Leeds", "Leipzig", "Lens", "Levante", "Leverkusen", "Lille", "Liverpool", "Lorient", "Lyon", "Mainz", "Man. City", "Man. United", "Marsella", "Milan", "Monza", "Moreirense", "Málaga", "Mónaco", "NEC", "Nacional", "Napoli", "Newcastle", "Niza", "Nott. Forest", "Osasuna", "PSG", "PSV", "Paderborn", "Paris FC", "Parma", "Porto", "R. Sociedad", "Racing", "Rayo", "Real Madrid", "Rennes", "Roma", "Sabah", "Santa Clara", "Sassuolo", "Schalke", "Sevilla", "Shakhtar", "Slavia Praga", "Slovan", "Sparta Rotterdam", "Sporting", "Sporting CP", "Stuttgart", "Sunderland", "Telstar", "Torino", "Tottenham", "Toulouse", "Troyes", "Twente", "Udinese", "Union Berlín", "Utrecht", "Valencia", "Venezia", "Viking", "Villarreal", "Vitória SC", "Willem II", "Zwolle"]}

# Equivalencias de nombres de la API -> nombres de la app (fragmento normalizado)
ALIAS = {"mancity": "Man. City", "manchestercity": "Man. City", "manutd": "Man. United",
         "manchesterunited": "Man. United", "nottmforest": "Nott. Forest",
         "nottinghamforest": "Nott. Forest", "realsociedad": "R. Sociedad",
         "deportivoalaves": "Alavés", "lacoruna": "Deportivo", "barca": "Barcelona",
         "atleti": "Atlético", "parissaintgermain": "PSG", "psg": "PSG", "parisfc": "Paris FC",
         "marseille": "Marsella", "strasbourg": "Estrasburgo", "nice": "Niza",
         "freiburg": "Friburgo", "koln": "Colonia", "cologne": "Colonia", "hamburg": "Hamburgo",
         "internazionale": "Inter", "brugge": "Brujas", "bruges": "Brujas",
         "slaviaprague": "Slavia Praga", "slaviapraha": "Slavia Praga", "aekathens": "AEK Atenas"}


def norm(x):
    x = unicodedata.normalize("NFKD", (x or "").lower()).encode("ascii", "ignore").decode()
    return "".join(c for c in x if c.isalnum())


SIN_EQUIVALENCIA = set()


def canon(t, liga):
    claves = {norm(k): k for k in TEAMS[liga]}
    nombres = [norm(t.get("shortName")), norm(t.get("name")), norm(t.get("tla"))]
    nombres = [n for n in nombres if n]
    for n in nombres:                                   # 1. igual
        if n in claves:
            return claves[n]
    for n in nombres[:2]:                               # 2. equivalencias
        for a in sorted(ALIAS, key=len, reverse=True):
            if a in n and norm(ALIAS[a]) in claves:
                return ALIAS[a]
    for n in nombres[:2]:                               # 3. contiene
        c = [k for k in claves if len(k) >= 4 and k in n]
        if c:
            return claves[max(c, key=len)]
    for n in nombres[:2]:                               # 4. parecido
        c = difflib.get_close_matches(n, list(claves), n=1, cutoff=0.82)
        if c:
            return claves[c[0]]
    nombre_api = t.get("shortName") or t.get("name") or "?"
    SIN_EQUIVALENCIA.add(f"{liga}: {nombre_api}")
    return nombre_api


def get(path):
    time.sleep(7)  # el plan gratuito permite 10 llamadas por minuto
    req = urllib.request.Request(BASE + path, headers={"X-Auth-Token": KEY})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def local(m):
    return datetime.fromisoformat(m["utcDate"].replace("Z", "+00:00")).astimezone(MAD)


def liga(k, code):
    hoy = datetime.now(MAD).date()
    st = get(f"/competitions/{code}/standings")["standings"]
    grupo = next((g for g in st if g.get("type") == "TOTAL"), st[0])
    tabla = ";".join(f'{canon(r["team"], k)}|{r["won"]}|{r["draw"]}|{r["lost"]}|{r["points"]}'
                     for r in grupo["table"])
    ini, fin = hoy - timedelta(days=9), hoy + timedelta(days=9)
    pasados = get(f"/competitions/{code}/matches?dateFrom={ini}&dateTo={hoy}")["matches"]
    futuros = get(f"/competitions/{code}/matches?dateFrom={hoy}&dateTo={fin}")["matches"]
    hechos = sorted((m for m in pasados if m["status"] == "FINISHED"), key=local)[-10:]
    proximos = sorted((m for m in futuros if m["status"] in ("SCHEDULED", "TIMED")), key=local)[:10]
    R = []
    for m in hechos:
        d, sc = local(m), m["score"]["fullTime"]
        R.append([canon(m["homeTeam"], k), canon(m["awayTeam"], k), sc["home"], sc["away"],
                  f"{DIAS[d.weekday()]} {d.day} {MESES[d.month - 1]}"])
    P = []
    for m in proximos:
        d = local(m)
        P.append([canon(m["homeTeam"], k), canon(m["awayTeam"], k), None, None, None,
                  f"{DIAS[d.weekday()]} {d.day} · {d:%H:%M}"])
    G = ""
    try:  # goleadores (si falla, se conservan los anteriores)
        G = ";".join(f'{x["player"]["name"]}|{canon(x["team"], k)}|{x["goals"]}'
                     for x in get(f"/competitions/{code}/scorers?limit=8")["scorers"])
    except Exception as e:
        print("Aviso: sin goleadores de", k, "->", e)
    out = {"R": R, "P": P, "S": tabla}
    if G:
        out["G"] = G
    return out


if __name__ == "__main__":
    try:
        datos = json.load(open("data.json", encoding="utf-8"))["leagues"]
    except Exception:
        datos = {}
    for k, code in LIGAS.items():
        try:
            datos[k] = liga(k, code)
            print("OK", k)
        except Exception as e:  # si una liga falla, se conservan los datos anteriores
            print("Aviso: no se pudo actualizar", k, "->", e)
    if SIN_EQUIVALENCIA:
        print("Nombres sin equivalencia en la app (envíamelos para añadirlos):", sorted(SIN_EQUIVALENCIA))
    if not datos:
        sys.exit("No se pudo actualizar ninguna liga")
    ahora = datetime.now(MAD)
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump({"updated": ahora.isoformat(timespec="minutes"),
                   "label": f"{ahora.day} {MESES[ahora.month - 1]}",
                   "leagues": datos}, f, ensure_ascii=False, indent=1)
