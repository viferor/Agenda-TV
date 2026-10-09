# Agenda TV

**Web:** https://agenda-tv-viferor.vercel.app/

Página web con dos vistas:

- **Agenda deportiva**: emisiones en directo de LaLiga (EA Sports e Hypermotion), UEFA Champions League, ciclismo, tenis y motor (solo Fórmula 1 y MotoGP). Se filtran por día y deporte, se ordenan por hora de emisión y muestran el canal y un enlace a la app oficial donde verlo (Movistar Plus+, DAZN, LaLiga TV, RTVE Play, Atresplayer, Mediaset Infinity, Eurosport…).
- **Parrilla TDT**: programación por horas de los canales nacionales de la TDT (sin los infantiles) más Canal Sur, en una línea de tiempo, con enlace a la app de cada cadena. Los canales se pueden marcar como favoritos (☆) y filtrar para ver solo esos; los favoritos se guardan en el navegador de cada dispositivo.

## Archivos

| Archivo | Qué es |
|---|---|
| `index.html` | La página (HTML, CSS y JS en un único archivo). Lee `datos.json`. |
| `build.py` | Descarga la guía XMLTV pública de [EPG dobleM](https://github.com/davidmuma/EPG_dobleM) y genera `datos.json`. |
| `datos.json` | Datos ya procesados (última generación). |
| `manifest.json`, `sw.js`, `iconos/` | Lo necesario para instalarla como app (PWA) y usarla sin conexión. |

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
- Motor: solo `Mundial F1` y `MotoGP` (fin de semana completo, incluidas Moto2 y Moto3); se descartan los programas previos y posteriores.
- La misma emisión en varios canales se agrupa en una sola entrada. Se omiten los canales para hostelería (BAR).

Los horarios son los de España peninsular y corresponden al inicio de la emisión.

## Publicar en Vercel

Es una web estática: no necesita build. En Vercel, *Add New → Project*, importa este repositorio con el preset **Other**, sin comando de build y con la raíz como directorio de salida. Cada commit en `main` (incluida la actualización diaria de `datos.json`) vuelve a desplegar la web automáticamente.

## Instalar como app (PWA)

- **Android (Chrome):** abre la web y pulsa *Instalar app* en la cabecera, o menú ⋮ → *Añadir a pantalla de inicio*.
- **iPhone (Safari):** botón Compartir → *Añadir a pantalla de inicio*.

La app pide siempre la guía más reciente a la red; sin conexión muestra la última que descargó. Mantén pulsado el icono para ir directamente a la *Agenda deportiva* o a la *Parrilla TDT*.
