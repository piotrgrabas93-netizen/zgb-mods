
import json
import os
import secrets

from flask import Flask, request, jsonify

app = Flask(__name__)

# =========================================================
# KATALOG MODÓW ZGB
# =========================================================

MODS = [
    {
        "id": "deutz-series9",
        "title": "Deutz-Fahr Series 9",
        "author": "Hacker",
        "category": "Ciagniki",
        "version": "2.1.0.0",
        "price_minor": 246000,
        "published": True,
        "purchased": True,
        "downloads": 0,
        "purchases": 0,
        "thumbnail": "https://i.postimg.cc/2VsgGp2F/icon-Deutz-Series9.png",
        "description": "Deutz-Fahr Series 9",
        "summary": "9290 / 9310 / 9340 TTV",
        "compatibility": "FS23 Mobile",
        "file_url": "https://files.catbox.moe/l6x1bh.zip",
        "filename": "FS22_DeutzSeries9.zip",
        "size_bytes": 13746831,
        "sha256": "68fafa7d51f41a268ee4adf5dd81b24e2049dc1d66e0b12c590d27e040a0ad39",
        "naffy_url": "",
        "tags": "",
        "changelog": "",
        "requirements": "",
        "gallery": [],
        "revision": 1,
        "updated_at": "2026-11-06T00:00:00+00:00",
    },

    {
        "id": "lindner-unitrac-pack",
        "title": "Lindner Unitrac Pack",
        "author": "Hacker",
        "category": "tiry",
        "version": "1.0.0.1",
        "price_minor": 153000,
        "published": True,
        "purchased": True,
        "downloads": 0,
        "purchases": 0,
        "thumbnail": "https://i.postimg.cc/2VsgGp2F/icon-Deutz-Series9.png",
        "description": "Lindner Unitrac Pack",
        "summary": "ADF 3200 Mistral 3400\nSwiss-Elite S 31\nPlatform",
        "compatibility": "FS23 Mobile",
        "file_url": "https://files.catbox.moe/3e3fhs.zip",
        "filename": "Lindner Unitrac Pack.zip",
        "size_bytes": 35441869,
        "sha256": "1b17b79c253b9884018e4ed620a10fc0aa97a4393589d7c0b7da4813e1ac26f2",
        "naffy_url": "",
        "tags": "",
        "changelog": "",
        "requirements": "",
        "gallery": [],
        "revision": 1,
        "updated_at": "2026-11-06T00:00:00+00:00",
    },
]


# =========================================================
# WIDOCZNE MODY
# =========================================================

def visible():
    return [m for m in MODS if m.get("published")]


# =========================================================
# KATALOG MODÓW
# =========================================================

def catalog_response():

    q = (request.args.get("q") or "").lower()
    cat = (request.args.get("category") or "").lower()
    filt = request.args.get("filter") or ""

    try:
        page = max(1, int(request.args.get("page") or 1))
    except ValueError:
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
    chunk = items[start:start + limit]

    out = []

    for m in chunk:
        row = dict(m)
        row.pop("file_url", None)
        out.append(row)

    return jsonify({
        "channel": {
            "revision": 1,
            "title": "ZGB",
            "video_id": ""
        },
        "items": out,
        "page": page,
        "page_size": limit,
        "total": len(items),
    })


# =========================================================
# GENEROWANIE KONTA
# =========================================================

def buyer():

    return jsonify({
        "token": "zgb-" + secrets.token_hex(16),
        "recovery_code": "ZGB-" + secrets.token_hex(6).upper(),
    })


@app.route("/v5/buyers", methods=["GET", "POST"])
@app.route("/buyers", methods=["GET", "POST"])
def buyers():
    return buyer()


@app.route("/v5/buyers/recover", methods=["GET", "POST"])
@app.route("/buyers/recover", methods=["GET", "POST"])
def recover():
    return buyer()


# =========================================================
# LISTA MODÓW
# =========================================================

@app.get("/v5/mods")
@app.get("/v5/mods/")
@app.get("/mods")
@app.get("/mods/")
def list_mods():
    return catalog_response()


@app.get("/v5")
@app.get("/v5/")
def v5_root():
    return catalog_response()


# =========================================================
# SZCZEGÓŁY MODA
# =========================================================

@app.get("/v5/mods/<mod_id>")
def one(mod_id):

    for m in visible():

        if m["id"] == mod_id:

            row = dict(m)
            row.pop("file_url", None)

            return jsonify(row)

    return jsonify({"error": "not found"}), 404


# =========================================================
# POBIERANIE MODA
# =========================================================

@app.post("/v5/mods/<mod_id>/download")
def download(mod_id):

    for m in visible():

        if m["id"] == mod_id:

            return jsonify({
                "uri": m.get("file_url", ""),
                "url": m.get("file_url", ""),
                "filename": m.get("filename", mod_id + ".zip"),
                "sha256": m.get("sha256", ""),
                "size_bytes": m.get("size_bytes", 0),
            })

    return jsonify({"error": "not found"}), 404

@app.get("/")
def root():

    return jsonify({
        "ok": True,
        "api": "/v5/mods"
    })

@app.route("/<path:path>", methods=["GET", "POST"])
def catch_all(path):

    if path.startswith("v5") or path.startswith("mods"):
        return catalog_response()

    return jsonify({
        "ok": True,
        "api": "/v5/mods"
    })


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )
