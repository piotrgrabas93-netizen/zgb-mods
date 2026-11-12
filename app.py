import os
import re
import html
import json
import hashlib
import threading
import urllib.request
import urllib.error
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

MEDIA = {
    "youtube": "https://www.youtube.com/@ZGB_Hacke_jp",
    "tiktok": "https://www.tiktok.com/@zgb_hacker._.zapa"
}

# TU USTAWIASZ CZAS AKTUALIZACJI (czas polski)
UPDATE_LABEL = "Aktualizacja za"
UPDATE_UNTIL = "01:00"

MODS = [
    {
        "id": "deutz-series9",
        "title": "Deutz-Fahr Series 9",
        "author": "Hacker",
        "category": "Ciagniki",
        "version": "2.1.0.0",
        "price_minor": 0,
        "published": True,
        "purchased": True,
        "downloads": 0,
        "purchases": 0,
        "thumbnail": "https://iili.io/ntb6QRa.png",
        "description": "Deutz-Fahr Series 9",
        "summary": "9290 / 9310 / 9340 TTV",
        "compatibility": "FS23 Mobile",
        "file_url": "https://www.mediafire.com/file/xhyvj8oqo21rjw6/FS22_DeutzSeries9.zip/file",
        "filename": "FS22_DeutzSeries9.zip",
        "size_bytes": 13746893,
        "sha256": "68fafa7d51f41a268ee4adf5dd81b24e2049dc1d66e0b12c590d27e040a0ad39",
        "naffy_url": "",
        "tags": "",
        "changelog": "",
        "requirements": "",
        "gallery": [],
        "revision": 1,
        "updated_at": "2026-11-06T00:00:00+00:00"
    },
    {
        "id": "lindner-unitrac-122",
        "title": "Lindner Unitrac 122 LDrive",
        "author": "Hacker",
        "category": "tiry",
        "version": "1.0.0.0",
        "price_minor": 0,
        "published": True,
        "purchased": True,
        "downloads": 0,
        "purchases": 0,
        "thumbnail": "https://iili.io/ntmdlB1.png",
        "description": "Lindner Unitrac 122 LDrive",
        "summary": "Unitrac 122 LDrive, ADF 3200, Mistral 3400 SR, Swiss-Elite S 31 Platform",
        "compatibility": "FS23 Mobile",
        "file_url": "https://www.mediafire.com/file/3onxgf34g2gvuwg/FS22_lindnerUnitrac122LDrive.zip/file",
        "filename": "lindnerUnitrac122LDrive.zip",
        "size_bytes": 15267267,
        "sha256": "1b17b79c253b9884018e4ed620a10fc0aa97a4393589d7c0b7da4813e1ac26f2",
        "naffy_url": "",
        "tags": "",
        "changelog": "",
        "requirements": "",
        "gallery": [],
        "revision": 1,
        "updated_at": "2026-11-06T00:00:00+00:00"
    },
    {
        "id": "LizardEnergy",
        "title": "Lizard Energy",
        "author": "Hacker",
        "category": "kosiarki",
        "version": "3.0.0.0",
        "price_minor": 0,
        "published": True,
        "purchased": True,
        "downloads": 0,
        "purchases": 0,
        "thumbnail": "https://iili.io/nDqwhGf.png",
        "description": "Lizard Energy",
        "summary": "Working width 1.5",
        "compatibility": "FS23 Mobile",
        "file_url": "https://www.mediafire.com/file/e2ysxbui14opltf/FS22_LizardEnergy.zip/file",
        "filename": "LizardEnergy.zip",
        "size_bytes": 9552527,
        "sha256": "137b12c4875b6853ae6471fd71eeccec8950b2fc80e8ef67c4eb630f36ed5979",
        "naffy_url": "",
        "tags": "",
        "changelog": "",
        "requirements": "",
        "gallery": [],
        "revision": 1,
        "updated_at": "2026-11-06T00:00:00+00:00"
    },
    {
        "id": "EVODISCK_Pack",
        "title": "EVODISCK Pack",
        "author": "Hacker",
        "category": "Kultywatory",
        "version": "2.1.0.0",
        "price_minor": 0,
        "published": True,
        "purchased": True,
        "downloads": 0,
        "purchases": 0,
        "thumbnail": "https://iili.io/nDCz7N1.png",
        "description": "EVODISCK Pack",
        "summary": "EVODISC-K 600\n-Base Price: 32.500",
        "compatibility": "FS23 Mobile",
        "file_url": "https://files.catbox.moe/2zstrz.zip",
        "filename": "EVODISCK_Pack.zip",
        "size_bytes": 33117956,
        "sha256": "26f35bd8455b781a9e0db4380cdeffcc8f32da2a7ffd511a0017913c10c67246",
        "naffy_url": "",
        "tags": "",
        "changelog": "",
        "requirements": "",
        "gallery": [],
        "revision": 1,
        "updated_at": "2026-11-06T00:00:00+00:00"
    },
    {
        "id": "amazoneZGB_ZGTS",
        "title": "amazoneZGB_ZGTS",
        "author": "Hacker",
        "category": "Kultywatory",
        "version": "1.1.0.0",
        "price_minor": 0,
        "published": True,
        "purchased": True,
        "downloads": 0,
        "purchases": 0,
        "thumbnail": "https://iili.io/nDmIDFI.png",
        "description": "amazoneZGB_ZGTS Pack",
        "summary": "Price 50000 Working width: 15.0-36.0 m",
        "compatibility": "FS23 Mobile",
        "file_url": "https://www.mediafire.com/file/cdabcke1t29r954/FS22_amazoneZGB_ZGTS.zip/file",
        "filename": "amazoneZGB_ZGTS.zip",
        "size_bytes": 5211423,
        "sha256": "80e9c66a7c6962f436cba95c16c32d0c53409e2563e33c128ebe10a24ae340b5",
        "naffy_url": "",
        "tags": "",
        "changelog": "",
        "requirements": "",
        "gallery": [],
        "revision": 1,
        "updated_at": "2026-11-06T00:00:00+00:00"
    },
    {
        "id": "JeantilBR10430",
        "title": "JeantilBR10430",
        "author": "Hacker",
        "category": "Przyczepy",
        "version": "1.0.0.0",
        "price_minor": 0,
        "published": True,
        "purchased": True,
        "downloads": 0,
        "purchases": 0,
        "thumbnail": "https://iili.io/nb2TYQt.png",
        "description": "JeantilBR10430 Pack",
        "summary": "Price 150.000 to 156.500 Capacity from 45.000 to 71.000 L",
        "compatibility": "FS23 Mobile",
        "file_url": "https://files.catbox.moe/i8ueiz.zip",
        "filename": "JeantilBR10430.zip",
        "size_bytes": 7769948,
        "sha256": "80e9c66a7c6962f436cba95c16c32d0c53409e2563e33c128ebe10a24ae340b5",
        "naffy_url": "",
        "tags": "",
        "changelog": "",
        "requirements": "",
        "gallery": [],
        "revision": 1,
        "updated_at": "2026-11-06T00:00:00+00:00"
    },
    {
        "id": "Lizard600",
        "title": "Lizard600",
        "author": "Hacker",
        "category": "obciazniki",
        "version": "1.0.0.0",
        "price_minor": 0,
        "published": True,
        "purchased": True,
        "downloads": 0,
        "purchases": 0,
        "thumbnail": "https://iili.io/nb2yYMP.png",
        "description": "Lizard600 Pack",
        "summary": "- Cena: 300 - Waga: 600 kg",
        "compatibility": "FS23 Mobile",
        "file_url": "https://files.catbox.moe/jpg5yy.zip",
        "filename": "Lizard600.zip",
        "size_bytes": 1929379,
        "sha256": "6bebee493303b2c5a4a3030cec6ce7167b4f6b3fb9441ef22ecdfff5b3efd4b7",
        "naffy_url": "",
        "tags": "",
        "changelog": "",
        "requirements": "",
        "gallery": [],
        "revision": 1,
        "updated_at": "2026-11-06T00:00:00+00:00"
    },
    {
        "id": "Fendt800VarioGen5",
        "title": "Fendt800VarioGen5",
        "author": "Hacker",
        "category": "Ciagniki",
        "version": "1.1.0.1",
        "price_minor": 0,
        "published": True,
        "purchased": True,
        "downloads": 0,
        "purchases": 0,
        "thumbnail": "https://iili.io/nba82iG.png",
        "description": "Fendt800VarioGen5",
        "summary": "Tractors Price 287,500€ Power 283 343 hp Max speed 40 60 kph",
        "compatibility": "FS23 Mobile",
        "file_url": "https://www.mediafire.com/file/6rdl8437n1k04fb/FS25_Fendt800VarioGen5.zip/file",
        "filename": "Fendt800VarioGen5.zip",
        "size_bytes": 34256998,
        "sha256": "192155899576ddf7d1b6e4c944948b5bb10f7a4feb4a64b69f458e5ff524a680",
        "naffy_url": "",
        "tags": "",
        "changelog": "",
        "requirements": "",
        "gallery": [],
        "revision": 1,
        "updated_at": "2026-11-06T00:00:00+00:00"
    },
    {
        "id": "Ursus4512_4514",
        "title": "Ursus4512_4514",
        "author": "Hacker",
        "category": "Ciagniki",
        "version": "1.1.0.0",
        "price_minor": 0,
        "published": True,
        "purchased": True,
        "downloads": 0,
        "purchases": 0,
        "thumbnail": "https://iili.io/nbaAbKQ.png",
        "description": "Ursus4512_4514",
        "summary": "Price 4512 31000 $ 4514 41000 $ Power 60 hp Max speed 28 kph",
        "compatibility": "FS23 Mobile",
        "file_url": "https://www.mediafire.com/file/t71w8y7vhuwpdcl/FS22_Ursus4512_4514.zip/file",
        "filename": "Ursus4512_4514.zip",
        "size_bytes": 34256998,
        "sha256": "4157181e853d9d2ad095b42cafc2846981f5221d3774e72d2e8aefbf4b322a2f",
        "naffy_url": "",
        "tags": "",
        "changelog": "",
        "requirements": "",
        "gallery": [],
        "revision": 1,
        "updated_at": "2026-11-06T00:00:00+00:00"
    }
]


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
    data = {m["id"]: int(m.get("downloads", 0)) for m in MODS}
    with open(COUNTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f)


def apply_counts():
    saved = load_counts()
    for m in MODS:
        if m["id"] in saved:
            m["downloads"] = int(saved[m["id"]])


def add_download(mod_id):
    with COUNTS_LOCK:
        for m in MODS:
            if m["id"] == mod_id:
                m["downloads"] = int(m.get("downloads", 0)) + 1
                save_counts()
                return m["downloads"]
    return 0


apply_counts()


def countdown_info():
    tz = timezone(timedelta(hours=1))
    try:
        dt = datetime.strptime(UPDATE_UNTIL, "%Y-%m-%d %H:%M").replace(tzinfo=tz)
        until_ms = int(dt.timestamp() * 1000)
        seconds = max(0, int(dt.timestamp() - datetime.now(tz).timestamp()))
    except Exception:
        until_ms = 0
        seconds = 0
    return {
        "label": UPDATE_LABEL,
        "until": UPDATE_UNTIL,
        "until_ms": until_ms,
        "seconds": seconds,
    }


def latest_video():
    try:
        url = (
            "https://www.youtube.com/feeds/videos.xml?channel_id="
            + CHANNEL_ID
        )
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=20) as response:
            xml = response.read().decode("utf-8", "ignore")
        vid = re.search(r"<yt:videoId>([^<]+)</yt:videoId>", xml)
        titles = re.findall(r"<title>(.*?)</title>", xml, re.DOTALL)
        video_id = vid.group(1) if vid else ""
        title = html.unescape(
            titles[1].strip() if len(titles) > 1 else "ZGB"
        )
        return {
            "video_id": video_id,
            "title": title,
            "thumbnail": (
                "https://img.youtube.com/vi/" + video_id + "/hqdefault.jpg"
            ) if video_id else "",
            "url": (
                "https://www.youtube.com/watch?v=" + video_id
            ) if video_id else ""
        }
    except Exception as e:
        print("YouTube error:", e)
        return {
            "video_id": "",
            "title": "ZGB",
            "thumbnail": "",
            "url": ""
        }


def visible():
    return [m for m in MODS if m.get("published", False)]


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
    raise Exception("Nie znaleziono bezpośredniego linku MediaFire")


def fetch_complete_file(mod):
    source_url = direct(mod.get("file_url", ""))
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
        content_type = upstream.headers.get("Content-Type", "").lower()
        if "text/html" in content_type:
            raise Exception("Źródło zwróciło HTML zamiast ZIP")
        expected = upstream.headers.get("Content-Length")
        data = BytesIO()
        received = 0
        while True:
            chunk = upstream.read(256 * 1024)
            if not chunk:
                break
            data.write(chunk)
            received += len(chunk)
        if expected:
            expected = int(expected)
            if received != expected:
                raise Exception(
                    "Niekompletny plik ze źródła. "
                    "Otrzymano " + str(received)
                    + " bajtów, oczekiwano " + str(expected)
                )
    file_data = data.getvalue()
    if not file_data:
        raise Exception("Pobrany plik jest pusty")
    buffer = BytesIO(file_data)
    if not zipfile.is_zipfile(buffer):
        raise Exception("Pobrany plik nie jest poprawnym ZIP-em")
    buffer.seek(0)
    with zipfile.ZipFile(buffer, "r") as archive:
        bad_file = archive.testzip()
        if bad_file:
            raise Exception("Uszkodzony plik w ZIP: " + bad_file)
    actual_size = len(file_data)
    actual_sha256 = hashlib.sha256(file_data).hexdigest()
    print("POPRAWNY ZIP:", mod["id"], actual_size, actual_sha256)
    return {
        "data": file_data,
        "size_bytes": actual_size,
        "sha256": actual_sha256,
        "filename": mod.get("filename", mod["id"] + ".zip")
    }


def get_file(mod):
    mod_id = mod["id"]
    with CACHE_LOCK:
        cached = FILE_CACHE.get(mod_id)
    if cached is not None:
        return cached
    downloaded = fetch_complete_file(mod)
    with CACHE_LOCK:
        FILE_CACHE[mod_id] = downloaded
    return downloaded


def catalog():
    q = (request.args.get("q") or "").lower().strip()
    cat = (request.args.get("category") or "").lower().strip()
    filt = request.args.get("filter") or ""
    try:
        page = max(1, int(request.args.get("page") or 1))
    except (ValueError, TypeError):
        page = 1
    limit = 40
    items = visible()
    if filt == "free":
        items = [m for m in items if m.get("price_minor", 0) == 0]
    elif filt == "paid":
        items = [m for m in items if m.get("price_minor", 0) > 0]
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
        "items": out,
        "page": page,
        "page_size": limit,
        "total": len(items)
    })


def load_help():
    if not os.path.exists(HELP_FILE):
        return []
    try:
        with open(HELP_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_help(items):
    with open(HELP_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False)


@app.get("/app.apk")
def app_apk():
    return redirect(APP_APK)


@app.get("/v5/channel/latest")
@app.get("/channel/latest")
def channel_latest():
    return jsonify(latest_video())


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


@app.get("/v5/mods/<mod_id>")
def one(mod_id):
    for m in visible():
        if m["id"] == mod_id:
            row = dict(m)
            row.pop("file_url", None)
            return jsonify(row)
    return jsonify({"error": "not found"}), 404


@app.route("/v5/mods/<mod_id>/download", methods=["GET", "POST"])
@app.route("/mods/<mod_id>/download", methods=["GET", "POST"])
def download(mod_id):
    mod = next((m for m in visible() if m["id"] == mod_id), None)
    if mod is None:
        return jsonify({"error": "not found"}), 404
    try:
        file_info = get_file(mod)
        add_download(mod_id)
        file_link = url_for("download_file", mod_id=mod_id, _external=True)
        return jsonify({
            "uri": file_link,
            "url": file_link,
            "filename": file_info["filename"],
            "sha256": file_info["sha256"],
            "size_bytes": file_info["size_bytes"]
        })
    except Exception as e:
        print("METADATA ERROR:", mod_id, repr(e))
        return jsonify({
            "error": "Nie udało się sprawdzić pliku",
            "details": str(e)
        }), 502


@app.get("/v5/mods/<mod_id>/file")
@app.get("/mods/<mod_id>/file")
def download_file(mod_id):
    mod = next((m for m in visible() if m["id"] == mod_id), None)
    if mod is None:
        return jsonify({"error": "not found"}), 404
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
            "attachment; filename*=UTF-8''" + quote(filename)
        )
        response.headers["Content-Length"] = str(file_info["size_bytes"])
        response.headers["Content-Transfer-Encoding"] = "binary"
        response.headers["Cache-Control"] = "no-store"
        response.headers["Accept-Ranges"] = "none"
        response.headers["X-Content-Type-Options"] = "nosniff"
        print("WYSŁANO:", mod_id, file_info["size_bytes"], file_info["sha256"])
        return response
    except Exception as e:
        print("DOWNLOAD ERROR:", mod_id, repr(e))
        return jsonify({
            "error": "Nie udało się pobrać kompletnego pliku",
            "details": str(e)
        }), 502


@app.route("/v5/help", methods=["GET", "POST"])
@app.route("/help", methods=["GET", "POST"])
def help_messages():
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        item = {
            "device_id": data.get("device_id", ""),
            "topic": data.get("topic", ""),
            "message": data.get("message", ""),
            "time": datetime.utcnow().isoformat()
        }
        with HELP_LOCK:
            items = load_help()
            items.append(item)
            save_help(items)
        return jsonify({"ok": True})
    device_id = request.args.get("device_id") or ""
    items = load_help()
    mine = [m for m in items if m.get("device_id") == device_id]
    return jsonify({"items": mine})


@app.get("/v5/help/all")
def help_all():
    items = load_help()
    page = "<html><meta charset='utf-8'><body style='background:#111;color:#eee;font-family:sans-serif;padding:16px'>"
    page += "<h2>Wiadomości z Pomocy</h2>"
    if not items:
        page += "<p>Brak wiadomości</p>"
    else:
        for m in items:
            line = (
                m.get("time", "")[:19].replace("T", " ")
                + " | "
                + m.get("topic", "")
                + " | "
                + m.get("message", "")
            )
            page += "<p>" + html.escape(line) + "</p>"
    page += "</body></html>"
    return page


@app.route("/v5/buyers", methods=["GET", "POST"])
@app.route("/buyers", methods=["GET", "POST"])
def buyers():
    return jsonify({
        "token": "zgb-ok",
        "recovery_code": "ZGB-OK"
    })


@app.get("/")
def root():
    return jsonify({
        "ok": True,
        "api": "/v5/mods",
        "latest_video": "/v5/channel/latest",
        "app_apk": "/app.apk",
        "media": MEDIA,
        "countdown": countdown_info()
    })


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        threaded=True)
