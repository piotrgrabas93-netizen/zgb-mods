
import os
import re
import json
import hashlib
import threading
import time
import zipfile
import urllib.request
import urllib.error

from io import BytesIO
from datetime import datetime, timezone, timedelta
from xml.etree import ElementTree

from flask import (
    Flask,
    request,
    jsonify,
    Response,
    redirect,
    send_file,
    abort
)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 500 * 1024 * 1024

# =========================================================
# USTAWIENIA
# =========================================================

CHANNEL_ID = "UC7oYer-vkZ7rvJTcy2onzrw"

APP_APK = "https://files.catbox.moe/7i882h.apk"

HELP_FILE = "help_messages.json"
DOWNLOADS_FILE = "downloads.json"
COUNTDOWN_FILE = "countdown_target.json"

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

LOCAL_TIMEZONE = timezone(timedelta(hours=1))

# =========================================================
# KATALOG MODÓW
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
    ),

    # =====================================================
    # NOWE MODY
    # =====================================================

    make_mod(
        "Lizard_PentaLine",
        "Lizard_PentaLine",
        "Ciagniki",
        "1.0.0.0",
        "https://iili.io/oH0YqNf.png",
        "Penta 7 Rows: Price: $ 23.000; Capacity: 350L of Seed, 450-750L Fertilizer; Work Area: 3,1 Meters; Power Requirement: 70 hp;",
        "https://www.mediafire.com/file/d520ly6yors4r4n/FS22_Lizard_PentaLine.zip/file",
        "Lizard_PentaLine.zip",
        "193dff6b09ebe0272fbdde20e0583f98334df354eecd1e899fbcfc8ec732fb6d"
    ),

    make_mod(
        "newHollandTX32",
        "newHollandTX32",
        "Kombajny",
        "1.0.0.0",
        "https://iili.io/oH0hmdv.png",
        "Price: 55.000 €Power: 155 hp Top speed: 25 kph",
        "https://www.mediafire.com/file/bj833xe5gr402t7/FS22_newHollandTX32.zip/file",
        "newHollandTX32.zip",
        "eab7f06ae5f1dfea2f10944cff5178d351e8419dc87d9c6332d7828aa4b8ce85"
    ),

    make_mod(
        "TLX3500_Series",
        "TLX3500_Series",
        "Samochody",
        "1.4.0.0",
        "https://iili.io/oH0ksXp.png",
        "TLX 3500 Series pick-up The Big Brother is here!!!! The TLX2020 set a standart in versatility, the TLX3500",
        "https://www.mediafire.com/file/b1zz7hdvkyjdxkm/FS22_TLX3500_Series.zip/file",
        "TLX3500_Series.zip",
        "a8945647a5b759bd39684de11a51d89c3e43583cd22558c1586bcfd8a2dfe766"
    )

]

# =========================================================
# PLIKI I LICZNIKI
# =========================================================

data_lock = threading.RLock()
cache_lock = threading.RLock()

file_cache = {}
file_cache_locks = {}


def read_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return default


def write_json(path, data):
    temporary = path + ".tmp"

    with open(temporary, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

    os.replace(temporary, path)


def load_download_counts():
    saved = read_json(DOWNLOADS_FILE, {})

    if not isinstance(saved, dict):
        saved = {}

    for mod in MODS:
        value = saved.get(mod["id"], mod.get("downloads", 0))

        try:
            mod["downloads"] = max(0, int(value))
        except (ValueError, TypeError):
            mod["downloads"] = 0


def save_download_counts():
    with data_lock:
        data = {
            mod["id"]: int(mod.get("downloads", 0))
            for mod in MODS
        }

        write_json(DOWNLOADS_FILE, data)


def add_download(mod):
    with data_lock:
        mod["downloads"] = int(mod.get("downloads", 0)) + 1
        save_download_counts()


load_download_counts()

# =========================================================
# LICZNIK AKTUALIZACJI
# =========================================================

def countdown_info():
    now = datetime.now(LOCAL_TIMEZONE)

    target_data = read_json(COUNTDOWN_FILE, {})
    if not isinstance(target_data, dict):
        target_data = {}

    key = f"{UPDATE_DAYS}:{UPDATE_HOURS}:{UPDATE_MINUTES}"

    until_ms = target_data.get("until_ms")

    if not isinstance(until_ms, (int, float)):
        until = now + timedelta(
            days=UPDATE_DAYS,
            hours=UPDATE_HOURS,
            minutes=UPDATE_MINUTES
        )

        until_ms = int(until.timestamp() * 1000)

        write_json(
            COUNTDOWN_FILE,
            {
                "key": key,
                "until_ms": until_ms
            }
        )

    remaining = max(
        0,
        int(until_ms / 1000 - now.timestamp())
    )

    days = remaining // 86400
    hours = (remaining % 86400) // 3600
    minutes = (remaining % 3600) // 60
    seconds = remaining % 60

    return {
        "label": UPDATE_LABEL,
        "days": days,
        "hours": hours,
        "minutes": minutes,
        "seconds": seconds,
        "remaining_seconds": remaining,
        "until_ms": until_ms
    }


# =========================================================
# YOUTUBE
# =========================================================

youtube_cache = {
    "updated": 0,
    "videos": []
}

YOUTUBE_CACHE_TTL = 300


def get_latest_videos():
    now = time.time()

    if (
        youtube_cache["videos"]
        and now - youtube_cache["updated"] < YOUTUBE_CACHE_TTL
    ):
        return youtube_cache["videos"]

    url = (
        "https://www.youtube.com/feeds/videos.xml"
        "?channel_id=" + CHANNEL_ID
    )

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            xml_data = response.read()

        root = ElementTree.fromstring(xml_data)

        namespace = {
            "atom": "http://www.w3.org/2005/Atom",
            "yt": "http://www.youtube.com/xml/schemas/2015"
        }

        videos = []

        for entry in root.findall("atom:entry", namespace):
            video_id = entry.findtext(
                "yt:videoId",
                default="",
                namespaces=namespace
            )

            title = entry.findtext(
                "atom:title",
                default="",
                namespaces=namespace
            )

            published = entry.findtext(
                "atom:published",
                default="",
                namespaces=namespace
            )

            if video_id:
                videos.append({
                    "id": video_id,
                    "title": title,
                    "published": published,
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "thumbnail": (
                        f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
                    )
                })

        youtube_cache["videos"] = videos
        youtube_cache["updated"] = now

        return videos

    except Exception:
        return youtube_cache["videos"]


# =========================================================
# POMOCNICZE
# =========================================================

def visible(mod):
    return bool(mod.get("published", True))


def find_mod(mod_id):
    for mod in MODS:
        if mod["id"] == mod_id and visible(mod):
            return mod

    return None


def public_mod(mod):
    result = dict(mod)

    # Nie ujawniamy wewnętrznego adresu źródłowego.
    result.pop("file_url", None)

    return result


def direct(url):
    if "mediafire.com/file/" not in url:
        return url

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )

    with urllib.request.urlopen(req, timeout=25) as response:
        html = response.read().decode(
            "utf-8",
            errors="ignore"
        )

    patterns = [
        r'href="(https://download[^"]+)"',
        r'"(https://download[^"]+)"',
        r'data-scrambled-url="([^"]+)"'
    ]

    for pattern in patterns:
        match = re.search(pattern, html)

        if match:
            link = match.group(1)

            if link.startswith("https://"):
                return link

    raise RuntimeError("Nie udało się pobrać bezpośredniego linku MediaFire.")


# =========================================================
# POBIERANIE I SPRAWDZANIE ZIP
# =========================================================

def fetch_complete_file(mod):
    url = direct(mod["file_url"])

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "*/*"
        }
    )

    with urllib.request.urlopen(req, timeout=120) as response:
        data = response.read()

        content_length = response.headers.get("Content-Length")

    if not data:
        raise RuntimeError("Pobrany plik jest pusty.")

    if content_length:
        try:
            expected_size = int(content_length)

            if len(data) != expected_size:
                raise RuntimeError(
                    "Pobrany plik ma nieprawidłowy rozmiar."
                )
        except ValueError:
            pass

    try:
        with zipfile.ZipFile(BytesIO(data), "r") as archive:
            bad_file = archive.testzip()

            if bad_file:
                raise RuntimeError(
                    f"Uszkodzony plik ZIP: {bad_file}"
                )

    except zipfile.BadZipFile:
        raise RuntimeError("Pobrany plik nie jest poprawnym archiwum ZIP.")

    actual_sha256 = hashlib.sha256(data).hexdigest()

    expected_sha256 = mod.get("sha256", "").strip().lower()

    if expected_sha256 and actual_sha256 != expected_sha256:
        raise RuntimeError(
            "Suma SHA256 pliku nie zgadza się z zapisaną w katalogu."
        )

    return {
        "data": data,
        "size": len(data),
        "sha256": actual_sha256,
        "filename": mod["filename"]
    }


def get_file(mod):
    mod_id = mod["id"]

    with cache_lock:
        if mod_id in file_cache:
            return file_cache[mod_id]

        if mod_id not in file_cache_locks:
            file_cache_locks[mod_id] = threading.Lock()

        mod_lock = file_cache_locks[mod_id]

    with mod_lock:
        with cache_lock:
            if mod_id in file_cache:
                return file_cache[mod_id]

        result = fetch_complete_file(mod)

        with cache_lock:
            file_cache[mod_id] = result

        mod["size_bytes"] = result["size"]

        return result


# =========================================================
# KATALOG
# =========================================================

def get_catalog():
    query = request.args.get("q", "").strip().lower()
    category = request.args.get("category", "").strip()

    free = request.args.get("free")
    paid = request.args.get("paid")

    try:
        page = max(1, int(request.args.get("page", 1)))
    except ValueError:
        page = 1

    try:
        page_size = int(request.args.get("page_size", 40))
        page_size = max(1, min(page_size, 100))
    except ValueError:
        page_size = 40

    items = [
        mod for mod in MODS
        if visible(mod)
    ]

    if query:
        items = [
            mod for mod in items
            if query in mod["title"].lower()
            or query in mod["description"].lower()
            or query in mod["summary"].lower()
            or query in mod["category"].lower()
        ]

    if category:
        items = [
            mod for mod in items
            if mod["category"].lower() == category.lower()
        ]

    if free in ("1", "true", "yes"):
        items = [
            mod for mod in items
            if int(mod.get("price_minor", 0)) == 0
        ]

    if paid in ("1", "true", "yes"):
        items = [
            mod for mod in items
            if int(mod.get("price_minor", 0)) > 0
        ]

    total = len(items)

    start = (page - 1) * page_size
    end = start + page_size

    selected = items[start:end]

    return {
        "channel_id": CHANNEL_ID,
        "media": MEDIA,
        "countdown": countdown_info(),
        "update": UPDATE,
        "items": [
            public_mod(mod) for mod in selected
        ],
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": (
            (total + page_size - 1) // page_size
        )
    }


# =========================================================
# APK
# =========================================================

@app.route("/app.apk")
def app_apk():
    return redirect(APP_APK, code=302)


# =========================================================
# KANAŁ / YOUTUBE
# =========================================================

@app.route("/v5/channel/latest")
@app.route("/channel/latest")
def channel_latest():
    return jsonify({
        "channel_id": CHANNEL_ID,
        "channel_url": MEDIA["youtube"],
        "videos": get_latest_videos()
    })


# =========================================================
# LISTA MODÓW
# =========================================================

@app.route("/v5/mods")
@app.route("/v5/mods/")
@app.route("/mods")
@app.route("/mods/")
def mods_list():
    return jsonify(get_catalog())


# =========================================================
# GŁÓWNY ENDPOINT V5
# =========================================================

@app.route("/v5")
@app.route("/v5/")
def api_v5():
    return jsonify({
        "success": True,
        "version": UPDATE["version"],
        "version_code": UPDATE["version_code"],
        "channel_id": CHANNEL_ID,
        "media": MEDIA,
        "countdown": countdown_info(),
        "update": UPDATE,
        "catalog": "/v5/mods",
        "latest_videos": "/v5/channel/latest"
    })


# =========================================================
# SZCZEGÓŁY MODA
# =========================================================

@app.route("/v5/mods/<mod_id>")
def mod_details(mod_id):
    mod = find_mod(mod_id)

    if not mod:
        return jsonify({
            "success": False,
            "error": "Mod nie istnieje."
        }), 404

    return jsonify({
        "success": True,
        "item": public_mod(mod)
    })


# =========================================================
# INFORMACJE O POBRANIU
# =========================================================

@app.route(
    "/v5/mods/<mod_id>/download",
    methods=["GET", "POST"]
)
@app.route(
    "/mods/<mod_id>/download",
    methods=["GET", "POST"]
)
def mod_download_info(mod_id):
    mod = find_mod(mod_id)

    if not mod:
        return jsonify({
            "success": False,
            "error": "Mod nie istnieje."
        }), 404

    return jsonify({
        "success": True,
        "uri": f"/v5/mods/{mod_id}/file",
        "url": f"/v5/mods/{mod_id}/file",
        "filename": mod["filename"],
        "sha256": mod["sha256"],
        "size_bytes": mod.get("size_bytes", 0)
    })


# =========================================================
# WŁAŚCIWE POBIERANIE PLIKU ZIP
# =========================================================

@app.route("/v5/mods/<mod_id>/file")
@app.route("/mods/<mod_id>/file")
def mod_file(mod_id):
    mod = find_mod(mod_id)

    if not mod:
        return jsonify({
            "success": False,
            "error": "Mod nie istnieje."
        }), 404

    try:
        result = get_file(mod)

        response = send_file(
            BytesIO(result["data"]),
            mimetype="application/zip",
            as_attachment=True,
            download_name=result["filename"],
            max_age=0
        )

        response.headers["Content-Length"] = str(result["size"])
        response.headers["X-Checksum-SHA256"] = result["sha256"]
        response.headers["Cache-Control"] = "no-store"

        add_download(mod)

        return response

    except urllib.error.HTTPError as error:
        return jsonify({
            "success": False,
            "error": "Błąd pobierania z serwera plików.",
            "details": str(error)
        }), 502

    except urllib.error.URLError as error:
        return jsonify({
            "success": False,
            "error": "Nie można połączyć się z serwerem plików.",
            "details": str(error)
        }), 502

    except Exception as error:
        return jsonify({
            "success": False,
            "error": "Nie udało się pobrać moda.",
            "details": str(error)
        }), 500


# =========================================================
# WIADOMOŚCI POMOCY
# =========================================================

@app.route("/v5/help", methods=["GET", "POST"])
@app.route("/help", methods=["GET", "POST"])
def help_messages():
    if request.method == "GET":
        messages = read_json(HELP_FILE, [])

        if not isinstance(messages, list):
            messages = []

        return jsonify({
            "success": True,
            "messages": messages
        })

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "error": "Nieprawidłowe dane JSON."
        }), 400

    message = str(
        data.get("message", "")
    ).strip()

    if not message:
        return jsonify({
            "success": False,
            "error": "Wiadomość nie może być pusta."
        }), 400

    messages = read_json(HELP_FILE, [])

    if not isinstance(messages, list):
        messages = []

    new_message = {
        "id": int(time.time() * 1000),
        "message": message,
        "name": str(data.get("name", "Użytkownik")),
        "created_at": datetime.now(
            timezone.utc
        ).isoformat()
    }

    messages.append(new_message)

    write_json(HELP_FILE, messages)

    return jsonify({
        "success": True,
        "message": new_message
    }), 201


# =========================================================
# WSZYSTKIE WIADOMOŚCI - HTML
# =========================================================

@app.route("/v5/help/all")
def help_all():
    messages = read_json(HELP_FILE, [])

    if not isinstance(messages, list):
        messages = []

    html = [
        "<!DOCTYPE html>",
        "<html lang='pl'>",
        "<head>",
        "<meta charset='UTF-8'>",
        "<meta name='viewport' content='width=device-width, initial-scale=1'>",
        "<title>ZGB Hacker - Wiadomości</title>",
        """
        <style>
        body {
            background: #111;
            color: white;
            font-family: Arial, sans-serif;
            padding: 20px;
        }
        .message {
            background: #222;
            border: 1px solid #444;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 12px;
        }
        .name {
            color: #e0b341;
            font-weight: bold;
        }
        .date {
            color: #999;
            font-size: 12px;
        }
        </style>
        """,
        "</head>",
        "<body>",
        "<h1>ZGB Hacker - Wiadomości</h1>"
    ]

    for item in reversed(messages):
        name = str(item.get("name", "Użytkownik"))
        message = str(item.get("message", ""))
        created = str(item.get("created_at", ""))

        # Zabezpieczenie przed wstrzyknięciem HTML.
        import html

        html.append(
            "<div class='message'>"
            f"<div class='name'>{html.escape(name)}</div>"
            f"<p>{html.escape(message)}</p>"
            f"<div class='date'>{html.escape(created)}</div>"
            "</div>"
        )

    html.extend([
        "</body>",
        "</html>"
    ])

    return Response(
        "\n".join(html),
        mimetype="text/html"
    )


# =========================================================
# BUYERS
# =========================================================

@app.route("/v5/buyers")
@app.route("/buyers")
def buyers():
    return jsonify({
        "token": "zgb-ok",
        "recovery_code": "ZGB-OK"
    })


# =========================================================
# STRONA GŁÓWNA
# =========================================================

@app.route("/")
def index():
    return jsonify({
        "success": True,
        "name": "ZGB Hacker API",
        "version": UPDATE["version"],
        "version_code": UPDATE["version_code"],
        "mods_count": len([
            mod for mod in MODS
            if visible(mod)
        ]),
        "endpoints": {
            "catalog": "/v5/mods",
            "mod_details": "/v5/mods/<mod_id>",
            "download_info": "/v5/mods/<mod_id>/download",
            "download_file": "/v5/mods/<mod_id>/file",
            "latest_videos": "/v5/channel/latest",
            "help": "/v5/help",
            "all_help": "/v5/help/all",
            "buyers": "/v5/buyers",
            "apk": "/app.apk"
        }
    })


# =========================================================
# OBSŁUGA BŁĘDÓW
# =========================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "Nie znaleziono endpointu."
    }), 404


@app.errorhandler(413)
def file_too_large(error):
    return jsonify({
        "success": False,
        "error": "Przesłany plik jest za duży."
    }), 413


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "error": "Wewnętrzny błąd serwera."
    }), 500


# =========================================================
# START SERWERA
# =========================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port,
        threaded=True)
