"""Prepara el proyecto Android generado por Capacitor para Android TV / Google TV.

- Añade la categoría LEANBACK_LAUNCHER para que la app salga en el inicio de la tele.
- Declara que no hacen falta pantalla táctil ni modo leanback (vale para móvil y tele).
- Añade el banner horizontal que Android TV muestra en su fila de apps.
Se ejecuta en GitHub Actions justo después de `npx cap add android`.
"""
import re, shutil, sys, pathlib

base = pathlib.Path(__file__).resolve().parent
man = base / "android/app/src/main/AndroidManifest.xml"
res = base / "android/app/src/main/res"
s = man.read_text(encoding="utf-8")

if "LEANBACK_LAUNCHER" not in s:
    s, n = re.subn(r'(\s*)(<category android:name="android.intent.category.LAUNCHER"\s*/>)',
                   r'\1\2\1<category android:name="android.intent.category.LEANBACK_LAUNCHER" />', s, count=1)
    assert n == 1, "no se encontró la categoría LAUNCHER"
if "android:banner" not in s:
    s, n = re.subn(r"<application\b", '<application\n        android:banner="@drawable/banner"', s, count=1)
    assert n == 1, "no se encontró <application>"
if "android.software.leanback" not in s:
    feats = ('    <uses-feature android:name="android.software.leanback" android:required="false" />\n'
             '    <uses-feature android:name="android.hardware.touchscreen" android:required="false" />\n')
    s = s.replace("    <application", feats + "    <application", 1) if "    <application" in s else s.replace("<application", feats + "<application", 1)
man.write_text(s, encoding="utf-8")

for folder, name in (("drawable", "banner.png"), ("drawable-xhdpi", "banner-xhdpi.png")):
    d = res / folder
    d.mkdir(parents=True, exist_ok=True)
    shutil.copy(base / "assets" / name, d / "banner.png")
print("Manifiesto preparado para Android TV")
