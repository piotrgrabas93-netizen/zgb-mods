import json, os, secrets
from flask import Flask, request, jsonify

app = Flask(__name__)

MODS = [
    {
        "id": "deutz-series9",
        "title": "Deutz-Fahr Series 9",
        "author": "RedCat3D",
        "category": "Ciagniki",
        "version": "2.1.0.0",
        "price_minor": 0,
        "published": True,
        "purchased": True,
        "downloads": 0,
        "purchases": 0,
        "thumbnail": "",
        "description": "Deutz-Fahr Series 9",
        "summary": "9290 / 9310 / 9340 TTV",
        "compatibility": "FS23 Mobile",
        "file_url": "https://TWOJ-LINK-DO-ZIP",
        "filename": "FS22_DeutzSeries9.zip",
        "size_bytes": 0,
        "sha256": "",
        "naffy_url": "",
        "tags": "",
        "changelog": "",
        "requirements": "",
        "gallery": [],
        "revision": 1,
        "updated_at": "2026-11-06T00:00:00+00:00",
    }
]

def visible():
    return [m for m in MODS if m.get("published")]

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
        items = [m for m in items if m.get("price_minor", 0) == 0]
    elif filt == "paid":
        items = [m for m in items if m.get("price_minor", 0) > 0]
    if q:
        items = [m for m in items if q in m.get("title", "").lower()]
    if cat:
        items = [m for m in items if cat in m.get("category", "").lower()]
    start = (page - 1) * limit
    chunk = items[start:start + limit]
    out = []
    for m in chunk:
        row = dict(m)
        row.pop("file_url", None)
        out.append(row)
    return jsonify({
        "channel": {"revision": 1, "title": "ZGB", "video_id": ""},
        "items": out,
        "page": page,
        "page_size": limit,
        "total": len(items),
    })

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

@app.get("/v5/mods/<mod_id>")
def one(mod_id):
    for m in visible():
        if m["id"] == mod_id:
            row = dict(m)
            row.pop("file_url", None)
            return jsonify(row)
    return jsonify({"error": "not found"}), 404

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
    return jsonify({"ok": True, "api": "/v5/mods"})

@app.route("/<path:path>", methods=["GET", "POST"])
def catch_all(path):
    if path.startswith("v5") or path.startswith("mods"):
        return catalog_response()
    return jsonify({"ok": True, "api": "/v5/mods"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
