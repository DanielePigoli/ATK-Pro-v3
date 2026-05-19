import requests, re
host = "archiviostatomodena.haltadefinizione.jarvis.memooria.org"
guid = "fec65c82-c3c2-47ed-8482-af4b0ec5f6a8"
g2 = "3fc901fe-7011-4b1f-ba3e-22274e540c5a"
g3 = "9216a85f-b621-4568-9379-6a12e3831c48"
tk = "45f1bde7-0666-4114-8bbb-bc037703ff33"
url = f"https://{host}/images/viewers/dzi/?multi={guid}_{g2}_{g3}&_t={tk}"
headers = {"User-Agent": "Mozilla/5.0"}
r = requests.get(url, headers=headers, timeout=10)
html = r.text
scripts = re.findall(r'src=[\"\x27](.*?\.js.*?)[\"\x27]', html)
for s in scripts[:5]:
    print("JS:", s)
for kw in ["tileSources", "dzi", "xmlPath", "apiUrl", "baseUrl", "imageUrl"]:
    found = re.findall(r".{0,80}" + kw + r".{0,80}", html)
    for f in found[:2]:
        print(kw+":", repr(f))
