
import os
import re
import html
import json
import hashlib
import threading
import time
import urllib.request
import zipfile

from io import BytesIO
from datetime import datetime, timezone, timedelta
from urllib.parse import quote
from flask import Flask, request, jsonify, Response, url_for, redirect

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 500 * 1024 * 1024

CHANNEL_ID = "UC7oYer-vkZ7rvJTcy2onzrw"
APP_APK = "https://files.catbox.moe/7i882h.apk"

FILE_CACHE = {}
CACHE_LOCK = threading.Lock()

HELP_FILE = "help_messages.json"
HELP_LOCK = threading.Lock()

COUNTS_FILE = "downloads.json"
COUNTS_LOCK = threading.Lock()

COUNTDOWN_FILE = "countdown_target.json"

VIDEO_CACHE = {"data": None, "time": 0}
VIDEO_LOCK = threading.Lock()
VIDEO_TTL = 300

MEDIA = {
    "youtube": "https://www.youtube.com/@ZGB_Hacke_jp",
    "tiktok": "https://www.tiktok.com/@zgb_hacker._.zapa",
    "discord": "https://discord.gg/UGKjzk2Zm"
}

UPDATE_LABEL = "Aktualizacja za"
UPDATE_DAYS = 99
UPDATE_HOURS = 50
UPDATE_MINUTES = 50

UPDATE = {
    "version_code": 5105,
    "version": "5.10.5",
    "message": "Czas minął. Zainstaluj nową wersję.",
    "apk_url": "https://files.catbox.moe/nhsc02.apk"
}


# =========================================================
# MODY
# =========================================================

def make_mod(
    mod_id,
    title,
    category,
    version,
    thumbnail,
    summary,
    file_url,
    filename,
    sha256
):
    return {
        "id": mod_id,
        "title": title,
        "author": "Hacker",
        "category": category,
        "version": version,
        "price_minor": 0,
        "published": True,
        "purchased": True,
        "downloads": 0,
        "purchases": 0,
        "thumbnail": thumbnail,
        "description": title,
        "summary": summary,
        "compatibility": "FS23 Mobile",
        "file_url": file_url,
        "filename": filename,
        "size_bytes": 0,
        "sha256": sha256,
        "naffy_url": "",
        "tags": "",
        "changelog": "",
        "requirements": "",
        "gallery": [],
        "revision": 1,
        "updated_at": "2026-11-06T00:00:00+00:00"
    }


MODS = [

    make_mod(
        "deutz-series9",
        "Deutz-Fahr Series 9",
        "Ciagniki",
        "2.1.0.0",
        "https://iili.io/ntb6QRa.png",
        "9290 / 9310 / 9340 TTV",
        "https://www.mediafire.com/file/xhyvj8oqo21rjw6/FS22_DeutzSeries9.zip/file",
        "FS22_DeutzSeries9.zip",
        "68fafa7d51f41a268ee4adf5dd81b24e2049dc1d66e0b12c590d27e040a0ad39"
    ),

    make_mod(
        "lindner-unitrac-122",
        "Lindner Unitrac 122 LDrive",
        "tiry",
        "1.0.0.0",
        "https://iili.io/ntmdlB1.png",
        "Unitrac 122 LDrive, ADF 3200, Mistral 3400 SR, Swiss-Elite S 31 Platform",
        "https://www.mediafire.com/file/3onxgf34g2gvuwg/FS22_lindnerUnitrac122LDrive.zip/file",
        "lindnerUnitrac122LDrive.zip",
        "1b17b79c253b9884018e4ed620a10fc0aa97a4393589d7c0b7da4813e1ac26f2"
    ),

    make_mod(
        "LizardEnergy",
        "Lizard Energy",
        "kosiarki",
        "3.0.0.0",
        "https://iili.io/nDqwhGf.png",
        "Working width 1.5",
        "https://www.mediafire.com/file/e2ysxbui14opltf/FS22_LizardEnergy.zip/file",
        "LizardEnergy.zip",
        "137b12c4875b6853ae6471fd71eeccec8950b2fc80e8ef67c4eb630f36ed5979"
    ),

    make_mod(
        "EVODISCK_Pack",
        "EVODISCK Pack",
        "Kultywatory",
        "2.1.0.0",
        "https://iili.io/nDCz7N1.png",
        "EVODISC-K 600\n-Base Price: 32.500",
        "https://files.catbox.moe/2zstrz.zip",
        "EVODISCK_Pack.zip",
        "26f35bd8455b781a9e0db4380cdeffcc8f32da2a7ffd511a0017913c10c67246"
    ),

    make_mod(
        "amazoneZGB_ZGTS",
        "amazoneZGB_ZGTS",
        "Kultywatory",
        "1.1.0.0",
        "https://iili.io/nDmIDFI.png",
        "Price 50000 Working width: 15.0-36.0 m",
        "https://www.mediafire.com/file/cdabcke1t29r954/FS22_amazoneZGB_ZGTS.zip/file",
        "amazoneZGB_ZGTS.zip",
        "80e9c66a7c6962f436cba95c16c32d0c53409e2563e33c128ebe10a24ae340b5"
    ),

    make_mod(
        "Lizard600",
        "Lizard600",
        "obciazniki",
        "1.0.0.0",
        "https://iili.io/nb2yYMP.png",
        "- Cena: 300 - Waga: 600 kg",
        "https://files.catbox.moe/jpg5yy.zip",
        "Lizard600.zip",
        "6bebee493303b2c5a4a3030cec6ce7167b4f6b3fb9441ef22ecdfff5b3efd4b7"
    ),

    make_mod(
        "Fendt800VarioGen5",
        "Fendt800VarioGen5",
        "Ciagniki",
        "1.1.0.1",
        "https://iili.io/nba82iG.png",
        "Tractors Price 287,500€ Power 283 343 hp Max speed 40 60 kph",
        "https://www.mediafire.com/file/6rdl8437n1k04fb/FS25_Fendt800VarioGen5.zip/file",
        "Fendt800VarioGen5.zip",
        "192155899576ddf7d1b6e4c944948b5bb10f7a4feb4a64b69f458e5ff524a680"
    ),

    make_mod(
        "Ursus4512_4514",
        "Ursus4512_4514",
        "Ciagniki",
        "1.1.0.0",
        "https://iili.io/nbaAbKQ.png",
        "Price 4512 31000 $ 4514 41000 $ Power 60 hp Max speed 28 kph",
        "https://www.mediafire.com/file/t71w8y7vhuwpdcl/FS22_Ursus4512_4514.zip/file",
        "Ursus4512_4514.zip",
        "4157181e853d9d2ad095b42cafc2846981f5221d3774e72d2e8aefbf4b322a2f"
    ),

    make_mod(
        "ClaasXerion12650",
        "ClaasXerion12650",
        "Ciagniki",
        "2.0.0.2",
        "https://i.ibb.co/QjKkkFNP/icon-Xerion12650.png",
        "Claas Xerion 12.650 Tractor, Large series tractor Model Xerion 12.590 Engine Price 706.045 $ Power 585HP",
        "https://www.mediafire.com/file/koqdyljjs04dme6/FS22_ClaasXerion12650.zip/file",
        "ClaasXerion12650.zip",
        "69d34ba6618d2d82aa223fbaf3cd1a3dbcb204f50d107ed81919465fd7c26979"
    ),

    make_mod(
        "MF600Series",
        "MF600Series",
        "Ciagniki",
        "1.1.1.0",
        "https://i.ibb.co/BVyDQp4y/icon-series600.png",
        "Base Price 600 Versions 2WD - 21.500$ 4WD - 26.500$",
        "https://www.mediafire.com/file/tf5zt9anpdawrz3/FS22_MF600Series.zip/file",
        "MF600Series.zip",
        "63615a618bbc349162eff06a4230c6ef10a847c76c28d6bac324d2fd9be5260e"
    ),

    make_mod(
        "URSUS_C360",
        "URSUS_C360",
        "Ciagniki",
        "1.0.0.0",
        "https://i.ibb.co/N6byzr1L/store-Ursus-C360.png",
        "Price: 18000 € Power: 45-52hp Category small tractors",
        "https://www.mediafire.com/file/rxquqzrcy1a0ds7/FS22_URSUS_C360.zip/file",
        "URSUS_C360.zip",
        "804daf4f2312324aa9666b064cecbfd696d77080300fd02ec5c6ddc1efd27b27"
    ),

    make_mod(
        "Big_Bud_747_16V",
        "Big_Bud_747_16V",
        "Ciagniki",
        "1.0.0.0",
        "https://iili.io/oHRGV9f.png",
        "Big Bud 747 16V Precio base: 406.500 € Potencia: 1100 cv",
        "https://www.mediafire.com/file/aw60l8e9dnfrubw/FS22_Big_Bud_747_16V.zip/file",
        "Big_Bud_747_16V.zip",
        "2557fea4ab77911ce0f5389735692e787789035bba0c36208a4a0fa8261254b9"
    ),

    make_mod(
        "ClaasTractor_Package",
        "ClaasTractor_Package",
        "Ciagniki",
        "1.1.1.0",
        "https://iili.io/oHRwPee.png",
        "Claas Arion 600 Price: 120.000 $ Power: 145 hp",
        "https://www.mediafire.com/file/972pyakiyvvyodg/FS22_ClaasTractor_Package.zip/file",
        "ClaasTractor_Package.zip",
        "80595da21f16be961e63e47f75ea81b70dabf3c6a261632e4049a10cf00beebd"
    ),

    make_mod(
        "Fendt800_900Favorit",
        "Fendt800_900Favorit",
        "Ciagniki",
        "1.1.1.0",
        "https://iili.io/oHRSyMu.png",
        "Prices: $76.000 / $81.500 Power: 165 - 265 HP / 165 - 285 HP Speed: 50 kph",
        "https://www.mediafire.com/file/lr6serbfxf0dvxz/FS22_Fendt800_900Favorit.zip/file",
        "Fendt800_900Favorit.zip",
        "9abd3ae44039fb0b2957ba8fe55378a4e3fc624b1a56733246eaed8b238408b8"
    ),

    make_mod(
        "FendtVarioPack",
        "FendtVarioPack",
        "Ciagniki",
        "2.0.0.0",
        "https://iili.io/oH5ekns.png",
        "200 series: 40 km/h $77.000 79 - 114 HP",
        "https://www.mediafire.com/file/9u8ejbb0pafzv0y/FS22_FendtVarioPack.zip/file",
        "FendtVarioPack.zip",
        "69c72532ae32c6d020196d3f853bdfec6ff3c38364037579519f92ba77a122ff"
    ),

    make_mod(
        "JohnDeere6R",
        "JohnDeere6R",
        "Ciagniki",
        "1.2.0.0",
        "https://iili.io/oH56NNR.png",
        "Base Price Small Chassis: 99.000 $ Medium Chassis: 128.000 $ Large Chassis: 171.000 $",
        "https://www.mediafire.com/file/uygkw41x7g17tez/FS22_JohnDeere6R.zip/file",
        "JohnDeere6R.zip",
        "088eaa2aeb61a112f349ec90539e34691da0954616e3aa705858c2800fa4da96"
    ),

    make_mod(
        "JohnDeere8r2016",
        "JohnDeere8r2016",
        "Ciagniki",
        "1.1.2.0",
        "https://iili.io/oH5pE3Q.png",
        "Price: $299,000 Power: 255-400 hp Max. speed: 50 kph",
        "https://www.mediafire.com/file/ms8zftc6klv90rs/FS22_JohnDeere8r2016.zip/file",
        "JohnDeere8r2016.zip",
        "0cba6657c00859ea526d55aae22cd983e7974685c39c445ed519bdf190dbe863"
    ),

    make_mod(
        "JohnDeere6010",
        "JohnDeere6010",
        "Ciagniki",
        "2.1.0.0",
        "https://iili.io/oH7otlS.png",
        "Price 4cyl: 50.000 $ Price 6cyl: 70.000 $ Power 80-185HP",
        "https://www.mediafire.com/file/pi1s4iaj7mx3p5t/FS22_JohnDeere6010.zip/file",
        "JohnDeere6010.zip",
        "a0455eefbe07737a3d898d4f54a44ee54a6a2cbbf7de481559c3cde389b7ba3a"
    ),

    make_mod(
        "JohnDeere7010Series",
        "JohnDeere7010Series",
        "Ciagniki",
        "1.0.3.0",
        "https://iili.io/oHYy2KG.png",
        "Power: 160-175 hp Price: $92,000",
        "https://www.mediafire.com/file/h4rny3u6af1d8v5/FS22_JohnDeere7010Series.zip/file",
        "JohnDeere7010Series.zip",
        "694805dd99a6d2862d9f7228f8e31e0f13e8ecf5f3b9c055efbc5bcf899adbff"
    ),

    make_mod(
        "JohnDeere8900series",
        "JohnDeere8900series",
        "Ciagniki",
        "1.0.0.0",
        "https://iili.io/oHaKYnp.png",
        "John Deere 8760 - 8960 Price: 79.999 € Power: 300HP - 370HP",
        "https://www.mediafire.com/file/kse3vxy7a3bream/FS22_JohnDeere8900series.zip/file",
        "JohnDeere8900series.zip",
        "2f9189b06512706aab828bbafd7a69c221a310d243df6bfdf21a49ccb2a187d2"
    )

]


# =========================================================
# LICZNIK POBRAŃ
# =========================================================

def load_counts():
    if not os.path.exists(COUNTS_FILE):
        return {}

    try:
        with open(COUNTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def save_counts():
    data = {
        m["id"]: int(m.get("downloads", 0))
        for m in MODS
    }

    temp_file = COUNTS_FILE + ".tmp"

    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump(data, f)

    os.replace(temp_file, COUNTS_FILE)


def apply_counts():
    saved = load_counts()

    for m in MODS:
        floor = int(m.get("downloads", 0))
        saved_value = int(saved.get(m["id"], 0))
        m["downloads"] = max(floor, saved_value)


def add_download(mod_id):
    with COUNTS_LOCK:
        for m in MODS:
            if m["id"] == mod_id:
                m["downloads"] = int(m.get("downloads", 0)) + 1

                try:
                    save_counts()
                except Exception as e:
                    print("COUNT SAVE ERROR:", repr(e))

                return m["downloads"]

    return 0


apply_counts()


# =========================================================
# LICZNIK AKTUALIZACJI
# =========================================================

def countdown_info():
    tz = timezone(timedelta(hours=1))
    now = datetime.now(tz)

    key = (
        str(UPDATE_DAYS) + ":"
        + str(UPDATE_HOURS) + ":"
        + str(UPDATE_MINUTES)
    )

    until_ms = 0
    saved = {}

    if os.path.exists(COUNTDOWN_FILE):
        try:
            with open(COUNTDOWN_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
        except Exception:
            saved = {}

    if saved.get("key") == key and saved.get("until_ms"):
        until_ms = int(saved["until_ms"])

    else:
        dt = now + timedelta(
            days=int(UPDATE_DAYS),
            hours=int(UPDATE_HOURS),
            minutes=int(UPDATE_MINUTES)
        )

        until_ms = int(dt.timestamp() * 1000)

        try:
            with open(COUNTDOWN_FILE, "w", encoding="utf-8") as f:
                json.dump({
                    "key": key,
                    "until_ms": until_ms
                }, f)
        except Exception as e:
            print("COUNTDOWN SAVE ERROR:", repr(e))

    seconds = max(
        0,
        int(until_ms / 1000 - now.timestamp())
    )

    return {
        "label": UPDATE_LABEL,
        "days": int(UPDATE_DAYS),
        "hours": int(UPDATE_HOURS),
        "minutes": int(UPDATE_MINUTES),
        "until_ms": until_ms,
        "seconds": seconds
    }


# =========================================================
# YOUTUBE
# =========================================================

def empty_video():
    return {
        "video_id": "",
        "title": "ZGB",
        "thumbnail": "",
        "url": ""
    }


def fetch_latest_video():
    url = (
        "https://www.youtube.com/feeds/videos.xml?channel_id="
        + CHANNEL_ID
    )

    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    with urllib.request.urlopen(req, timeout=8) as response:
        xml = response.read().decode("utf-8", "ignore")

    vid = re.search(
        r"<yt:videoId>([^<]+)</yt:videoId>",
        xml
    )

    titles = re.findall(
        r"<title>(.*?)</title>",
        xml,
        re.DOTALL
    )

    video_id = vid.group(1) if vid else ""

    title = html.unescape(
        titles[1].strip() if len(titles) > 1 else "ZGB"
    )

    return {
        "video_id": video_id,
        "title": title,
        "thumbnail": (
            "https://img.youtube.com/vi/"
            + video_id
            + "/hqdefault.jpg"
        ) if video_id else "",
        "url": (
            "https://www.youtube.com/watch?v="
            + video_id
        ) if video_id else ""
    }


def latest_video():
    now = time.time()

    with VIDEO_LOCK:
        cached = VIDEO_CACHE["data"]
        age = now - VIDEO_CACHE["time"]

        if cached is not None and age < VIDEO_TTL:
            return cached

    try:
        data = fetch_latest_video()

    except Exception as e:
        print("YouTube error:", repr(e))

        with VIDEO_LOCK:
            if VIDEO_CACHE["data"] is not None:
                return VIDEO_CACHE["data"]

        data = empty_video()

    with VIDEO_LOCK:
        VIDEO_CACHE["data"] = data
        VIDEO_CACHE["time"] = now

    return data


# =========================================================
# KATALOG
# =========================================================

def visible():
    return [
        m for m in MODS
        if m.get("published", False)
    ]


# =========================================================
# MEDIAFIRE - BEZPOŚREDNI LINK
# =========================================================

def direct(url):
    if "mediafire.com/file/" not in url:
        return url

    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    with urllib.request.urlopen(req, timeout=60) as response:
        page = response.read().decode("utf-8", "ignore")

    page = html.unescape(page)
    page = page.replace("\\/", "/")

    patterns = [
        r'https://download\d*\.mediafire\.com/[^"\'<>\s]+',
        r'"(https://download\d*\.mediafire\.com/[^"]+)"',
        r'href="(https://download\d*\.mediafire\.com/[^"]+)"'
    ]

    for pattern in patterns:
        found = re.findall(pattern, page)

        if found:
            return found[0].rstrip("\\")

    raise Exception(
        "Nie znaleziono bezpośredniego linku MediaFire"
    )


# =========================================================
# POBIERANIE I SPRAWDZANIE ZIP
# =========================================================

def fetch_complete_file(mod):
    source_url = direct(
        mod.get("file_url", "")
    )

    req = urllib.request.Request(
        source_url,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/zip,application/octet-stream,*/*",
            "Accept-Encoding": "identity",
            "Connection": "close"
        }
    )

    with urllib.request.urlopen(req, timeout=240) as upstream:

        content_type = upstream.headers.get(
            "Content-Type", ""
        ).lower()

        if "text/html" in content_type:
            raise Exception(
                "Źródło zwróciło HTML zamiast ZIP"
            )

        expected = upstream.headers.get("Content-Length")

        data = BytesIO()
        received = 0

        while True:
            chunk = upstream.read(256 * 1024)

            if not chunk:
                break

            data.write(chunk)
            received += len(chunk)

            if received > 500 * 1024 * 1024:
                raise Exception(
                    "Plik przekracza limit 500 MB"
                )

        if expected:
            expected = int(expected)

            if received != expected:
                raise Exception(
                    "Niekompletny plik ze źródła. "
                    "Otrzymano "
                    + str(received)
                    + " bajtów, oczekiwano "
                    + str(expected)
                )

    file_data = data.getvalue()

    if not file_data:
        raise Exception("Pobrany plik jest pusty")

    buffer = BytesIO(file_data)

    if not zipfile.is_zipfile(buffer):
        raise Exception(
            "Pobrany plik nie jest poprawnym ZIP-em"
        )

    buffer.seek(0)

    with zipfile.ZipFile(buffer, "r") as archive:

        bad_file = archive.testzip()

        if bad_file:
            raise Exception(
                "Uszkodzony plik w ZIP: " + bad_file
            )

    actual_size = len(file_data)

    actual_sha256 = hashlib.sha256(
        file_data
    ).hexdigest()

    print(
        "POPRAWNY ZIP:",
        mod["id"],
        actual_size,
        actual_sha256
    )

    return {
        "data": file_data,
        "size_bytes": actual_size,
        "sha256": actual_sha256,
        "filename": mod.get(
            "filename",
            mod["id"] + ".zip"
        )
    }


# =========================================================
# CACHE PLIKÓW
# =========================================================

def get_file(mod):
    mod_id = mod["id"]

    with CACHE_LOCK:
        cached = FILE_CACHE.get(mod_id)

    if cached is not None:
        return cached

    downloaded = fetch_complete_file(mod)

    with CACHE_LOCK:
        if mod_id not in FILE_CACHE:
            FILE_CACHE[mod_id] = downloaded

        return FILE_CACHE[mod_id]


# =========================================================
# KATALOG API
# =========================================================

def catalog():
    q = (
        request.args.get("q") or ""
    ).lower().strip()

    cat = (
        request.args.get("category") or ""
    ).lower().strip()

    filt = request.args.get("filter") or ""

    try:
        page = max(
            1,
            int(request.args.get("page") or 1)
        )
    except (ValueError, TypeError):
        page = 1

    limit = 40

    items = visible()

    if filt == "free":
        items = [
            m for m in items
            if m.get("price_minor", 0) == 0
        ]

    elif filt == "paid":
        items = [
            m for m in items
            if m.get("price_minor", 0) > 0
        ]

    if q:
        items = [
            m for m in items
            if q in m.get("title", "").lower()
            or q in m.get("category", "").lower()
            or q in m.get("summary", "").lower()
        ]

    if cat:
        items = [
            m for m in items
            if cat in m.get("category", "").lower()
        ]

    start = (page - 1) * limit

    out = []

    for m in items[start:start + limit]:
        row = dict(m)
        row.pop("file_url", None)
        out.append(row)

    return jsonify({
        "channel": latest_video(),
        "media": MEDIA,
        "countdown": countdown_info(),
        "update": UPDATE,
        "items": out,
        "page": page,
        "page_size": limit,
        "total": len(items)
    })


# =========================================================
# POMOC - WIADOMOŚCI
# =========================================================

def load_help():
    if not os.path.exists(HELP_FILE):
        return []

    try:
        with open(HELP_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

            return data if isinstance(data, list) else []

    except Exception as e:
        print("HELP LOAD ERROR:", repr(e))
        return []


def save_help(items):
    temp_file = HELP_FILE + ".tmp"

    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump(
            items,
            f,
            ensure_ascii=False
        )

    os.replace(temp_file, HELP_FILE)


# =========================================================
# APK
# =========================================================

@app.get("/app.apk")
def app_apk():
    return redirect(APP_APK)


# =========================================================
# YOUTUBE API
# =========================================================

@app.get("/v5/channel/latest")
@app.get("/channel/latest")
def channel_latest():
    return jsonify(latest_video())


# =========================================================
# LISTA MODÓW
# =========================================================

@app.get("/v5/mods")
@app.get("/v5/mods/")
@app.get("/mods")
@app.get("/mods/")
def list_mods():
    return catalog()


@app.get("/v5")
@app.get("/v5/")
def v5_root():
    return catalog()


# =========================================================
# POJEDYNCZY MOD
# =========================================================

@app.get("/v5/mods/<mod_id>")
def one(mod_id):
    for m in visible():

        if m["id"] == mod_id:
            row = dict(m)
            row.pop("file_url", None)

            return jsonify(row)

    return jsonify({
        "error": "not found"
    }), 404


# =========================================================
# INFORMACJE O POBIERANIU
# =========================================================

@app.route(
    "/v5/mods/<mod_id>/download",
    methods=["GET", "POST"]
)
@app.route(
    "/mods/<mod_id>/download",
    methods=["GET", "POST"]
)
def download(mod_id):

    mod = next(
        (m for m in visible() if m["id"] == mod_id),
        None
    )

    if mod is None:
        return jsonify({
            "error": "not found"
        }), 404

    try:
        file_info = get_file(mod)

        file_link = url_for(
            "download_file",
            mod_id=mod_id,
            _external=True
        )

        return jsonify({
            "uri": file_link,
            "url": file_link,
            "filename": file_info["filename"],
            "sha256": file_info["sha256"],
            "size_bytes": file_info["size_bytes"]
        })

    except Exception as e:

        print(
            "METADATA ERROR:",
            mod_id,
            repr(e)
        )

        return jsonify({
            "error": "Nie udało się sprawdzić pliku",
            "details": str(e)
        }), 502


# =========================================================
# WŁAŚCIWE POBIERANIE ZIP
# =========================================================

@app.get("/v5/mods/<mod_id>/file")
@app.get("/mods/<mod_id>/file")
def download_file(mod_id):

    mod = next(
        (m for m in visible() if m["id"] == mod_id),
        None
    )

    if mod is None:
        return jsonify({
            "error": "not found"
        }), 404

    try:
        file_info = get_file(mod)

        file_data = file_info["data"]
        filename = file_info["filename"]

        response = Response(
            file_data,
            status=200,
            content_type="application/zip"
        )

        response.headers["Content-Disposition"] = (
            "attachment; filename*=UTF-8''"
            + quote(filename)
        )

        response.headers["Content-Length"] = str(
            file_info["size_bytes"]
        )

        response.headers["Content-Transfer-Encoding"] = "binary"
        response.headers["Cache-Control"] = "no-store"
        response.headers["Accept-Ranges"] = "none"
        response.headers["X-Content-Type-Options"] = "nosniff"

        add_download(mod_id)

        print(
            "WYSŁANO:",
            mod_id,
            file_info["size_bytes"],
            file_info["sha256"]
        )

        return response

    except Exception as e:

        print(
            "DOWNLOAD ERROR:",
            mod_id,
            repr(e)
        )

        return jsonify({
            "error": "Nie udało się pobrać kompletnego pliku",
            "details": str(e)
        }), 502


# =========================================================
# SYSTEM POMOCY
# =========================================================

@app.route(
    "/v5/help",
    methods=["GET", "POST"]
)
@app.route(
    "/help",
    methods=["GET", "POST"]
)
def help_messages():

    if request.method == "POST":

        data = request.get_json(silent=True) or {}

        if not isinstance(data, dict):
            return jsonify({
                "error": "Nieprawidłowe dane"
            }), 400

        device_id = str(
            data.get("device_id", "")
        ).strip()

        topic = str(
            data.get("topic", "")
        ).strip()

        message = str(
            data.get("message", "")
        ).strip()

        if not device_id or not message:
            return jsonify({
                "error": "Brakuje device_id lub message"
            }), 400

        if len(device_id) > 200:
            return jsonify({
                "error": "device_id jest za długi"
            }), 400

        if len(topic) > 200:
            return jsonify({
                "error": "Temat jest za długi"
            }), 400

        if len(message) > 10000:
            return jsonify({
                "error": "Wiadomość jest za długa"
            }), 400

        item = {
            "device_id": device_id,
            "topic": topic,
            "message": message,
            "time": datetime.now(
                timezone.utc
            ).isoformat()
        }

        with HELP_LOCK:
            items = load_help()
            items.append(item)

            try:
                save_help(items)
            except Exception as e:
                print("HELP SAVE ERROR:", repr(e))

                return jsonify({
                    "error": "Nie udało się zapisać wiadomości"
                }), 500

        return jsonify({
            "ok": True
        })

    device_id = request.args.get(
        "device_id"
    ) or ""

    with HELP_LOCK:
        items = load_help()

    mine = [
        m for m in items
        if m.get("device_id") == device_id
    ]

    return jsonify({
        "items": mine
    })


# =========================================================
# WSZYSTKIE WIADOMOŚCI - PANEL
# =========================================================

@app.get("/v5/help/all")
def help_all():

    with HELP_LOCK:
        items = load_help()

    page = (
        "<html>"
        "<meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width, initial-scale=1'>"
        "<body style='background:#111;color:#eee;"
        "font-family:sans-serif;padding:16px'>"
    )

    page += "<h2>Wiadomości z Pomocy</h2>"

    if not items:
        page += "<p>Brak wiadomości</p>"

    else:
        for m in items:

            line = (
                str(m.get("time", ""))[:19].replace("T", " ")
                + " | "
                + str(m.get("topic", ""))
                + " | "
                + str(m.get("message", ""))
            )

            page += (
                "<p style='background:#202020;"
                "padding:12px;border-radius:8px'>"
                + html.escape(line)
                + "</p>"
            )

    page += "</body></html>"

    return Response(
        page,
        content_type="text/html; charset=utf-8"
    )


# =========================================================
# BUYERS
# =========================================================

@app.route(
    "/v5/buyers",
    methods=["GET", "POST"]
)
@app.route(
    "/buyers",
    methods=["GET", "POST"]
)
def buyers():

    return jsonify({
        "token": "zgb-ok",
        "recovery_code": "ZGB-OK"
    })


# =========================================================
# STRONA GŁÓWNA API
# =========================================================

@app.get("/")
def root():

    return jsonify({
        "ok": True,
        "api": "/v5/mods",
        "latest_video": "/v5/channel/latest",
        "app_apk": "/app.apk",
        "media": MEDIA,
        "countdown": countdown_info(),
        "update": UPDATE
    })


# =========================================================
# START SERWERA
# =========================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        threaded=True
    )
