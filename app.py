
import os
import re
import urllib.request
from flask import Flask, request, jsonify

app = Flask(__name__)

CHANNEL_ID = "UC7oYer-vkZ7rvJTcy2onzrw"

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
        "id": "ursus_1614_Pack",
        "title": "ursus 1614 pack",
        "author": "Hacker",
        "category": "male ciagniki",
        "version": "1.5.0.0",
        "price_minor": 0,
        "published": True,
        "purchased": True,
        "downloads": 0,
        "purchases": 0,
        "thumbnail": "https://iili.io/nDo6N9t.png",
        "description": "ursus_1614_Pack",
        "summary": "Price: 58000 Power 155 Max speed 28/38 kph",
        "compatibility": "FS23 Mobile",
        "file_url": "https://files.catbox.moe/zl3iec.zip",
        "filename": "ursus_1614_Pack.zip",
        "size_bytes": 44900127,
        "sha256": "333296c3f22e4b951f9c45487989f53284e5d218e5b9e662941d6e2ba9903da8",
        "naffy_url": "",
        "tags": "",
        "changelog": "",
        "requirements": "",
        "gallery": [],
        "revision": 1,
        "updated_at": "2026-11-06T00:00:00+00:00"
}.



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

        vid = re.search(
            r"<yt:videoId>([^<]+)</yt:videoId>",
            xml
        )

        title = re.findall(
            r"<title>(.*?)</title>",
            xml
        )

        return {
            "video_id": vid.group(1) if vid else "",
            "title": title[1] if len(title) > 1 else "ZGB"
        }

    except Exception as e:
        print("YouTube error:", e)

        return {
            "video_id": "",
            "title": "ZGB"
        }


def visible():
    return [
        m for m in MODS
        if m.get("published")
    ]


def direct(url):
    if "mediafire.com/file/" not in url:
        return url

    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        with urllib.request.urlopen(req, timeout=30) as response:
            html = response.read().decode("utf-8", "ignore")

        found = re.findall(
            r"https://download\d*\.mediafire\.com[^\"'<> ]+",
            html
        )

        return found[0] if found else url

    except Exception as e:
        print("MediaFire error:", e)
        return url


def catalog():
    q = (request.args.get("q") or "").lower()
    cat = (request.args.get("category") or "").lower()
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
        "items": out,
        "page": page,
        "page_size": limit,
        "total": len(items)
    })


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

    return jsonify({
        "error": "not found"
    }), 404


@app.route(
    "/v5/mods/<mod_id>/download",
    methods=["GET", "POST"]
)
@app.route(
    "/mods/<mod_id>/download",
    methods=["GET", "POST"]
)
def download(mod_id):
    for m in visible():
        if m["id"] == mod_id:
            link = direct(
                m.get("file_url", "")
            )

            return jsonify({
                "uri": link,
                "url": link,
                "filename": m.get(
                    "filename",
                    mod_id + ".zip"
                ),
                "sha256": m.get("sha256", ""),
                "size_bytes": m.get("size_bytes", 0)
            })

    return jsonify({
        "error": "not found"
    }), 404


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


@app.get("/")
def root():
    return jsonify({
        "ok": True,
        "api": "/v5/mods"
    })


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))    )
