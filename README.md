# Agenda TV

Página web con dos vistas:

- **Agenda deportiva**: emisiones en directo de LaLiga (EA Sports e Hypermotion), UEFA Champions League, ciclismo y tenis. Se filtran por día y deporte, se ordenan por hora de emisión y muestran el canal y un enlace a la app oficial donde verlo (Movistar Plus+, DAZN, LaLiga TV, RTVE Play, Eurosport…).
- **Parrilla TVE**: programación por horas de La 1, La 2, 24h, Teledeporte y Clan en una línea de tiempo.

## Archivos

| Archivo | Qué es |
|---|---|
| `index.html` | La página (HTML, CSS y JS en un único archivo). Lee `datos.json`. |
| `build.py` | Descarga la guía XMLTV pública de [EPG dobleM](https://github.com/davidmuma/EPG_dobleM) y genera `datos.json`. |
| `datos.json` | Datos ya procesados (última generación). |

## Actualizar los datos

```bash
python3 build.py --descargar datos.json     # descarga la guía y genera datos.json
python3 build.py guiatv.xml datos.json      # o a partir de una guía ya descargada
```

Solo usa la biblioteca estándar de Python 3.

## Cómo se clasifican las emisiones

- Solo cuentan los programas cuyo título empieza por `DIRECTO` (se descartan reposiciones, previas y magacines).
- LaLiga: categoría *Fútbol* y título con `LALIGA EA SPORTS` o `LALIGA HYPERMOTION`.
- Champions: categoría *Fútbol* y título con `UEFA Champions League`.
- Ciclismo / Tenis: por la categoría de la guía.
- La misma emisión en varios canales se agrupa en una sola entrada. Se omiten los canales para hostelería (BAR).

Los horarios son los de España peninsular y corresponden al inicio de la emisión.
