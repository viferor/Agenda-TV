# Agenda TV

**Web:** https://agenda-tv-viferor.vercel.app/

Página web con tres vistas:

- **Agenda deportiva**: emisiones en directo de LaLiga (EA Sports e Hypermotion), UEFA Champions League, ciclismo, tenis y motor (solo Fórmula 1 y MotoGP). Se filtran por día y deporte, se ordenan por hora de emisión y muestran el canal y un enlace a la app oficial donde verlo (Movistar Plus+, DAZN, LaLiga TV, RTVE Play, Atresplayer, Mediaset Infinity, Eurosport…).
- **Parrilla TDT**: programación por horas de los canales nacionales de la TDT (sin los infantiles) más Canal Sur, Replay (sustituto gratuito de Gol, de Mediapro) y DBike, en una línea de tiempo, con enlace a la app de cada cadena. Los canales se pueden marcar como favoritos (☆) y filtrar para ver solo esos; los favoritos se guardan en el navegador de cada dispositivo. También hay filtros de contenido: cine, series, deportes, documentales, infantiles, noticias, música y otros.
- **Movistar Plus+**: la misma línea de tiempo con todo el dial de la plataforma: los canales propios (Movistar Plus, M+ Estrenos, M+ LaLiga, M+ Deportes, M+ Cine, M+ Documentales…), los multievento (M+ LaLiga 3–6, M+ Liga de Campeones 2–13, M+ Deportes 3–8, M+ Baloncesto 2–5, M+ Vamos 2–3) y las versiones HDR/UHD, además del resto del dial: DAZN (LaLiga, F1, MotoGP, Baloncesto, 1–4), LaLiga TV Hypermotion, Eurosport 1 y 2, TCM, AXN, Warner TV, Comedy Central, Calle 13, Cosmo, SciFi, STAR, BBC, National Geographic, Discovery, Caza y Pesca, Disney, Nickelodeon, Clan, MTV, Mezzo, las autonómicas, las noticias internacionales y un largo etcétera (157 canales). No repite los canales de la TDT, que ya están en su pestaña. Cada programa tiene su ficha (sinopsis, reparto, año, nota, edad) y un botón a la app de su cadena. Tiene sus propios favoritos (☆), filtros de contenido y filtro de favoritos, independientes de los de la TDT. Para ver estos canales hace falta suscripción: la web solo muestra la guía.

## Archivos

| Archivo | Qué es |
|---|---|
| `index.html` | La página (HTML, CSS y JS en un único archivo). Lee `datos.json` y, al abrir la pestaña de Movistar Plus+, `datos-mplus.json`. |
| `build.py` | Descarga la guía XMLTV pública de [EPG dobleM](https://github.com/davidmuma/EPG_dobleM) y genera los dos archivos de datos. |
| `datos.json` | Agenda deportiva y parrilla de la TDT (última generación). |
| `datos-mplus.json` | Parrilla del dial de Movistar Plus+ (última generación). Va aparte porque son casi 10 MB y así la página no los descarga si no se abre esa pestaña. |
| `manifest.json`, `sw.js`, `iconos/` | Lo necesario para instalarla como app (PWA) y usarla sin conexión. |

## Actualizar los datos

```bash
python3 build.py --descargar datos.json     # descarga la guía y genera los dos archivos
python3 build.py guiatv.xml datos.json      # o a partir de una guía ya descargada
```

Solo usa la biblioteca estándar de Python 3. El segundo argumento es la salida principal; al lado escribe el otro archivo, con el sufijo `-mplus` (`datos.json` → `datos-mplus.json`). **Los dos se tienen que subir al repositorio**: si el script diario hace `git add datos.json`, hay que añadir también `datos-mplus.json` (o usar `git add -A`).

`datos.json` tiene estas claves: `generado`, `fuente`, `eventos` (agenda deportiva) y `tve` (parrilla de la TDT). `datos-mplus.json` tiene `generado`, `fuente` y `mplus` (parrilla de Movistar Plus+). Las dos parrillas comparten formato:

```json
{ "id": "id XMLTV del canal", "name": "nombre visible", "app": "app oficial", "url": "enlace",
  "cat": "cine|series|deportes|docs|infantil|noticias|musica|otros",
  "p": [ { "t": "título", "s": "inicio", "e": "fin", "g": "Género · Subgénero",
           "opcionales": "d sinopsis, y año, r nota, a edad, sn serie, se temporada, ep episodio, et título del episodio, c créditos" } ] }
```

`cat` es la categoría del canal para los filtros de contenido. Sale de la tabla `CAT_RULES` de `build.py` (las familias conocidas: DAZN, M+ LaLiga, TCM, Clan, CNN…) y, si el canal no encaja en ninguna, del género que más minutos ocupa en la guía; las franjas de relleno sin género no cuentan. Si falta el campo, la página lo deduce igualmente a partir de los géneros, así que un `datos.json` antiguo sigue funcionando.

Los canales de la parrilla no se deducen de la guía: están en las constantes `TVE` y `MOVISTAR` de `build.py`, en el orden en que se quieren ver. `MOVISTAR` es el dial completo en su orden, menos los canales de la TDT (que ya están en `TVE`). Si la guía cambia un nombre o añade un canal, se edita esa lista y se vuelve a generar. Un canal que no traiga programación no se publica (no queda una fila vacía), así que los feeds que solo emiten algunos días aparecen y desaparecen solos. Si sobran canales, se borran sus líneas y se regenera.

La 1 HD tiene que seguir siendo el primer canal de `tve`: la página lo usa para saber qué días hay parrilla.

## Cómo se clasifican las emisiones

- Solo cuentan los programas cuyo título empieza por `DIRECTO` (se descartan reposiciones, previas y magacines) y las franjas `TBC` de Movistar Plus+, que son directos cuyos partidos aún no se han anunciado (aparecen como «Partidos por confirmar»).
- LaLiga: categoría *Fútbol* y título con `LALIGA EA SPORTS` o `LALIGA HYPERMOTION`.
- Champions: categoría *Fútbol* y título con `UEFA Champions League`.
- Ciclismo / Tenis: por la categoría de la guía.
- Motor: solo `Mundial F1` y `MotoGP` (fin de semana completo, incluidas Moto2 y Moto3); se descartan los programas previos y posteriores.
- La misma emisión en varios canales se agrupa en una sola entrada. Se omiten los canales para hostelería (BAR).
- La parrilla (TDT y Movistar Plus+) no se filtra: muestra todo lo que emite cada canal, sea directo o no.

## Gratis en otros países

Al elegir un deporte aparece un apartado informativo con las cadenas extranjeras que lo emiten en abierto, con el enlace a su web oficial. Es una lista fija (constante `GRATIS` en `index.html`), revisada en octubre de 2026: hay que actualizarla cuando cambien los derechos. Esas emisiones solo se pueden ver desde el país de cada cadena.

Los horarios son los de España peninsular y corresponden al inicio de la emisión.

## Publicar en Vercel

Es una web estática: no necesita build. En Vercel, *Add New → Project*, importa este repositorio con el preset **Other**, sin comando de build y con la raíz como directorio de salida. Cada commit en `main` (incluida la actualización diaria de los datos) vuelve a desplegar la web automáticamente.

## Instalar como app (PWA)

- **Android (Chrome):** abre la web y pulsa *Instalar app* en la cabecera, o menú ⋮ → *Añadir a pantalla de inicio*.
- **iPhone (Safari):** botón Compartir → *Añadir a pantalla de inicio*.

La app pide siempre la guía más reciente a la red; sin conexión muestra la última que descargó. La parrilla de Movistar Plus+ se guarda al instalar la app y, si no cupo, la primera vez que se abre esa pestaña. Mantén pulsado el icono para ir directamente a la *Agenda deportiva*, a la *Parrilla TDT* o a *Movistar Plus+* (atajos `#agenda`, `#tdt` y `#mplus`).
