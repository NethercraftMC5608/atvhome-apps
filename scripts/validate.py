#!/usr/bin/env python3
"""Validate catalog.json: fields, unique ids, and (with --download) each package's hash and contents."""
import hashlib, json, plistlib, re, sys, tempfile, urllib.request, zipfile

REQUIRED = ["id", "name", "version", "package", "sha256"]
errors = []
cat = json.load(open("catalog.json"))
apps = cat.get("apps")
if not isinstance(apps, list):
    sys.exit("catalog.json: 'apps' must be a list")
seen = set()
for i, a in enumerate(apps):
    where = f"apps[{i}] ({a.get('id', '?')})"
    for k in REQUIRED:
        if not isinstance(a.get(k), str) or not a[k]:
            errors.append(f"{where}: missing '{k}'")
    if a.get("id") in seen:
        errors.append(f"{where}: duplicate id")
    seen.add(a.get("id"))
    if not re.fullmatch(r"\d+(\.\d+)*", a.get("version", "")):
        errors.append(f"{where}: version must be dotted numbers")
    if not a.get("package", "").startswith("https://"):
        errors.append(f"{where}: package must be an https URL")
    if not re.fullmatch(r"[0-9a-f]{64}", a.get("sha256", "")):
        errors.append(f"{where}: sha256 must be 64 lowercase hex digits")
    if "--download" in sys.argv and not errors:
        data = urllib.request.urlopen(a["package"], timeout=60).read()
        if hashlib.sha256(data).hexdigest() != a["sha256"]:
            errors.append(f"{where}: sha256 doesn't match the download"); continue
        with tempfile.TemporaryFile() as t:
            t.write(data); t.seek(0)
            z = zipfile.ZipFile(t)
            tops = {n.split("/")[0] for n in z.namelist() if not n.startswith("__MACOSX")}
            bundles = [n for n in tops if n.endswith(".tvapp")]
            if len(bundles) != 1:
                errors.append(f"{where}: zip must contain exactly one .tvapp"); continue
            info = plistlib.loads(z.read(f"{bundles[0]}/Info.plist"))
            if info.get("CFBundleIdentifier") != a["id"]:
                errors.append(f"{where}: Info.plist id is {info.get('CFBundleIdentifier')}")
            if str(info.get("CFBundleShortVersionString") or info.get("CFBundleVersion")) != a["version"]:
                errors.append(f"{where}: Info.plist version doesn't match")
            if not info.get("NSPrincipalClass"):
                errors.append(f"{where}: Info.plist has no NSPrincipalClass")
for e in errors:
    print("error:", e)
print(f"{len(apps)} apps, {len(errors)} errors")
sys.exit(1 if errors else 0)
