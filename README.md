# Agenda TV

**Web:** https://agenda-tv-viferor.vercel.app/

Página web con tres vistas:

- **Agenda deportiva**: emisiones en directo de LaLiga (EA Sports e Hypermotion), UEFA Champions League, ciclismo, tenis y motor (solo Fórmula 1 y MotoGP). Se filtran por día y deporte, se ordenan por hora de emisión y muestran el canal y un enlace a la app oficial donde verlo (Movistar Plus+, DAZN, LaLiga TV, RTVE Play, Atresplayer, Mediaset Infinity, Eurosport…).
- **Parrilla TDT**: programación por horas de los canales nacionales de la TDT (sin los infantiles) más La Séptima (el canal nuevo de la TDT desde el 5 de noviembre de 2026, con su directo gratis en YouTube), Canal Sur, Replay (sustituto gratuito de Gol, de Mediapro) y DBike, en una línea de tiempo, con enlace a la app de cada cadena. Los canales se pueden marcar como favoritos (☆) y filtrar para ver solo esos; los favoritos se guardan en el navegador de cada dispositivo. También hay filtros de contenido: cine, series, deportes, documentales, infantiles, noticias, música y otros.
- **Movistar Plus+**: la misma línea de tiempo con todo el dial de la plataforma: los canales propios (Movistar Plus, M+ Estrenos, M+ LaLiga, M+ Deportes, M+ Cine, M+ Documentales…), los multievento (M+ LaLiga 3–6, M+ Liga de Campeones 2–13, M+ Deportes 3–8, M+ Baloncesto 2–5, M+ Vamos 2–3) y las versiones HDR/UHD, además del resto del dial: DAZN (LaLiga, F1, MotoGP, Baloncesto, 1–4), LaLiga TV Hypermotion, Eurosport 1 y 2, TCM, AXN, Warner TV, Comedy Central, Calle 13, Cosmo, SciFi, STAR, BBC, National Geographic, Discovery, Caza y Pesca, Disney, Nickelodeon, Clan, MTV, Mezzo, las autonómicas, las noticias internacionales y un largo etcétera (158 canales). No repite los canales de la TDT, que ya están en su pestaña, salvo La Séptima, que Movistar Plus+ ofrece en el dial 7. Cada programa tiene su ficha (sinopsis, reparto, año, nota, edad) y un botón a la app de su cadena. Tiene sus propios favoritos (☆), filtros de contenido y filtro de favoritos, independientes de los de la TDT. Para ver estos canales hace falta suscripción: la web solo muestra la guía.

- **Buscador**: la caja de arriba busca a la vez en canales, partidos de la agenda y programas de las dos parrillas, sin distinguir mayúsculas ni tildes y desde ahora hasta el final de la guía. Los programas coinciden por título, serie, episodio, dirección o reparto (por ejemplo, el nombre de un actor). Al tocar un resultado se abre la ficha del programa, el partido en la agenda o el canal en su parrilla.

## Archivos

| Archivo | Qué es |
|---|---|
| `index.html` | La página (HTML, CSS y JS en un único archivo). Lee `datos.json` y, al abrir la pestaña de Movistar Plus+, `datos-mplus.json`. |
| `build.py` | Descarga la guía XMLTV pública de [EPG dobleM](https://github.com/davidmuma/EPG_dobleM) y genera los dos archivos de datos. |
| `datos.json` | Agenda deportiva y parrilla de la TDT (última generación). |
| `datos-mplus.json` | Parrilla del dial de Movistar Plus+ (última generación). Va aparte porque son casi 10 MB y así la página no los descarga si no se abre esa pestaña. |
| `manifest.json`, `sw.js`, `iconos/` | Lo necesario para instalarla como app (PWA) y usarla sin conexión. |

## Actualizar los datos

**Automático:** el flujo de trabajo [`.github/workflows/datos.yml`](.github/workflows/datos.yml) regenera los dos archivos y los sube a `main` cuatro veces al día (08:10, 12:10, 16:10 y 20:10 UTC, diez minutos después de cada publicación de la guía de dobleM). No hay que hacer nada: cuando llega un commit nuevo, Vercel vuelve a desplegar la web con la guía del día. También se puede lanzar a mano desde la pestaña *Actions* del repositorio (*Run workflow*). Si el `git push` del flujo falla con un 403, hay que activar en GitHub *Settings → Actions → General → Workflow permissions* la opción **Read and write permissions**.

**Desde la web:** el botón **«↻ Actualizar»** de la cabecera vuelve a pedir la guía y la parrilla en ese momento, sin caché, para no tener que recargar la página.

**A mano** (solo si quieres forzar una actualización):

```bash
python3 build.py --descargar datos.json     # descarga la guía y genera los dos archivos
python3 build.py guiatv.xml datos.json      # o a partir de una guía ya descargada
```

Solo usa la biblioteca estándar de Python 3. El segundo argumento es la salida principal; al lado escribe el otro archivo, con el sufijo `-mplus` (`datos.json` → `datos-mplus.json`). **Los dos se tienen que subir al repositorio**: si haces `git add datos.json`, añade también `datos-mplus.json` (o usa `git add -A`).

Si se sube uno y el otro no, la web no se rompe: la pestaña de Movistar Plus+ avisa de que su parrilla es de otra fecha (y dice hasta qué día llega) con un botón para recargarla, y la agenda y la TDT siguen funcionando con `datos.json`. La página pide siempre los datos y la parrilla con `cache: "no-store"`, así que nunca se queda con una copia vieja del navegador.

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

## App Android (APK)

En [Releases](https://github.com/viferor/Agenda-TV/releases) está la APK para móviles y Android TV. Es una app hecha con Capacitor (carpeta `app-android/`) que abre la web de Vercel, así que la guía y los cambios de la web llegan sin reinstalar. Los enlaces a otras webs (YouTube, RTVE Play, Movistar Plus+…) se abren en su app o en el navegador.

La compila GitHub Actions (`.github/workflows/apk.yml`): al subir una etiqueta `vX.Y.Z` crea la release con `AgendaTV-X.Y.Z.apk`. Se firma siempre con la misma clave para que cada versión se instale encima de la anterior; la clave va en los secretos `ANDROID_KEYSTORE_B64` y `ANDROID_KEYSTORE_PASSWORD` del repositorio, nunca en el código.

## Instalar como app (PWA)

- **Android (Chrome):** abre la web y pulsa *Instalar app* en la cabecera, o menú ⋮ → *Añadir a pantalla de inicio*.
- **iPhone (Safari):** botón Compartir → *Añadir a pantalla de inicio*.

La app pide siempre la guía más reciente a la red; sin conexión muestra la última que descargó. La parrilla de Movistar Plus+ se guarda al instalar la app y, si no cupo, la primera vez que se abre esa pestaña. Mantén pulsado el icono para ir directamente a la *Agenda deportiva*, a la *Parrilla TDT* o a *Movistar Plus+* (atajos `#agenda`, `#tdt` y `#mplus`).
