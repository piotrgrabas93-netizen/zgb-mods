import json, os
from flask import Flask, request, jsonify, redirect

app = Flask(__name__)

# Wpisz tu swoje mody. price_minor: 0 = darmowy.
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
        "thumbnail": "",
        "description": "Deutz-Fahr Series 9",
        "summary": "9290 / 9310 / 9340 TTV",
        "compatibility": "FS23 Mobile",
        "file_url": "https://www.mediafire.com/file/xhyvj8oqo21rjw6/FS22_DeutzSeries9.zip/file",
        "filename": "FS22_DeutzSeries9.zip",
        "size_bytes":13746831,
        "sha256": "68fafa7d51f41a268ee4adf5dd81b24e2049dc1d66e0b12c590d27e040a0ad39",
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

@app.get("/v5/mods")
def list_mods():
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

@app.route("/v5/mods/<mod_id>/download", methods=["GET", "POST"])
@app.route("/mods/<mod_id>/download", methods=["GET", "POST"])
def download(mod_id):
    for m in visible():
        if m["id"] == mod_id:
            link = m.get("file_url", "")
            return jsonify({
                "uri": link,
                "url": link,
                "filename": m.get("filename", mod_id + ".zip"),
                "sha256": m.get("sha256", ""),
                "size_bytes": m.get("size_bytes", 0),
            })
    return jsonify({"error": "not found"}), 404

@app.get("/")
def root():
    return jsonify({"ok": True, "api": "/v5/mods"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
