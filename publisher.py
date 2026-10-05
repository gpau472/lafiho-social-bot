#!/usr/bin/env python3
"""LAFIHO social bot · publica en Instagram y Facebook lo que está APROBADO y vencido.

Uso:
  python publisher.py            # publica lo vencido y aprobado
  python publisher.py --dry-run  # solo muestra qué haría (no llama a la API)
Variables de entorno (secrets de GitHub):
  Instagram (API con inicio de sesión de Instagram):  IG_TOKEN, IG_USER_ID
  Facebook (opcional, más adelante):                  PAGE_TOKEN, PAGE_ID
"""
import os, sys, json, glob, time, mimetypes
from datetime import datetime, timezone
import requests

DRY = "--dry-run" in sys.argv
FB_GRAPH = "https://graph.facebook.com/v21.0"
# Si hay IG_TOKEN se usa la API de Instagram con inicio de sesión de Instagram (no necesita página de Facebook)
if os.environ.get("IG_TOKEN"):
    GRAPH = "https://graph.instagram.com/v21.0"
    TOKEN = os.environ["IG_TOKEN"]
else:
    GRAPH = FB_GRAPH
    TOKEN = os.environ.get("PAGE_TOKEN", "")
FB_TOKEN = os.environ.get("PAGE_TOKEN", "")
IG = os.environ.get("IG_USER_ID", "")
PAGE = os.environ.get("PAGE_ID", "")
REPO = os.environ.get("GITHUB_REPOSITORY", "USUARIO/REPO")
BRANCH = os.environ.get("GITHUB_REF_NAME", "main")
RAW = os.environ.get("RAW_BASE", f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/")
MAX_ATTEMPTS = 3


def raw(path):
    return RAW + path.lstrip("/")


def call(method, url, **kw):
    if DRY:
        print(f"   [dry-run] {method} {url} {json.dumps(kw.get('data') or kw.get('params') or {}, ensure_ascii=False)[:160]}")
        return {"id": "DRY-RUN"}
    r = requests.request(method, url, timeout=180, **kw)
    try:
        data = r.json()
    except Exception:
        data = {"raw": r.text[:300]}
    if r.status_code >= 400 or "error" in data:
        raise RuntimeError(f"{method} {url.split('?')[0]} -> {r.status_code} {json.dumps(data, ensure_ascii=False)[:400]}")
    return data


def wait_container(cid, tries=40):
    if DRY:
        return
    for _ in range(tries):
        d = requests.get(f"{GRAPH}/{cid}", params={"fields": "status_code,status", "access_token": TOKEN}, timeout=60).json()
        sc = d.get("status_code")
        if sc == "FINISHED":
            return
        if sc in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"contenedor {cid}: {d}")
        time.sleep(6)
    raise RuntimeError(f"contenedor {cid}: tiempo agotado")


def ig_publish(container):
    wait_container(container)
    return call("POST", f"{GRAPH}/{IG}/media_publish", data={"creation_id": container, "access_token": TOKEN})


def ig_resumable_video(kind, path, caption):
    """Reels/Stories en vídeo: subida resumable (no necesita URL pública)."""
    body = {"media_type": kind, "upload_type": "resumable", "access_token": TOKEN}
    if caption:
        body["caption"] = caption
    if kind == "REELS":
        body["share_to_feed"] = "true"
    c = call("POST", f"{GRAPH}/{IG}/media", data=body)
    if DRY:
        return c["id"]
    size = os.path.getsize(path)
    with open(path, "rb") as f:
        up = requests.post(c["uri"], headers={"Authorization": f"OAuth {TOKEN}", "offset": "0", "file_size": str(size)}, data=f, timeout=900)
    if up.status_code >= 400:
        raise RuntimeError(f"subida resumable: {up.status_code} {up.text[:300]}")
    return c["id"]


def post_instagram(item):
    t, files, cap = item["type"], item["files"], item.get("caption", "")
    if t == "post":
        c = call("POST", f"{GRAPH}/{IG}/media", data={"image_url": raw(files[0]), "caption": cap, "access_token": TOKEN})
        return ig_publish(c["id"])
    if t == "carousel":
        kids = [call("POST", f"{GRAPH}/{IG}/media", data={"image_url": raw(f), "is_carousel_item": "true", "access_token": TOKEN})["id"] for f in files]
        c = call("POST", f"{GRAPH}/{IG}/media", data={"media_type": "CAROUSEL", "children": ",".join(kids), "caption": cap, "access_token": TOKEN})
        return ig_publish(c["id"])
    if t == "reel":
        cid = ig_resumable_video("REELS", files[0], cap)
        return ig_publish(cid)
    if t == "story":
        f = files[0]
        if f.lower().endswith((".mp4", ".mov")):
            cid = ig_resumable_video("STORIES", f, "")
        else:
            cid = call("POST", f"{GRAPH}/{IG}/media", data={"media_type": "STORIES", "image_url": raw(f), "access_token": TOKEN})["id"]
        return ig_publish(cid)
    raise ValueError(f"tipo desconocido: {t}")


def post_facebook(item):
    t, files, cap = item["type"], item["files"], item.get("caption", "")
    if t == "post":
        return call("POST", f"{FB_GRAPH}/{PAGE}/photos", data={"url": raw(files[0]), "caption": cap, "access_token": FB_TOKEN})
    if t == "carousel":
        ids = [call("POST", f"{FB_GRAPH}/{PAGE}/photos", data={"url": raw(f), "published": "false", "access_token": FB_TOKEN})["id"] for f in files]
        att = {f"attached_media[{i}]": json.dumps({"media_fbid": x}) for i, x in enumerate(ids)}
        return call("POST", f"{FB_GRAPH}/{PAGE}/feed", data={"message": cap, "access_token": FB_TOKEN, **att})
    if t == "reel":
        return call("POST", f"{FB_GRAPH}/{PAGE}/videos", data={"file_url": raw(files[0]), "description": cap, "access_token": FB_TOKEN})
    print("   (las historias no se replican en Facebook automáticamente)")
    return {"id": "skipped"}


def main():
    now = datetime.now(timezone.utc)
    changed = False
    for fp in sorted(glob.glob("schedule/*.json")):
        week = json.load(open(fp, encoding="utf-8"))
        for it in week["items"]:
            if it.get("status", "pending") != "pending" or not it.get("approved"):
                continue
            when = datetime.fromisoformat(it["when"])
            if when > now:
                continue
            print(f"▶ {it['id']} ({it['type']}) programado {it['when']}")
            if it.get("manual"):
                print("   requiere pegatina manual: no se publica por API")
                continue
            for f in it["files"]:
                if not os.path.exists(f):
                    it["status"], it["error"] = "error", f"falta el archivo {f}"
            if it.get("status") == "error":
                changed = True
                continue
            res = {}
            try:
                if "instagram" in it.get("platforms", ["instagram"]):
                    res["instagram"] = post_instagram(it).get("id")
                if "facebook" in it.get("platforms", []):
                    if not (PAGE and FB_TOKEN):
                        raise RuntimeError("Facebook no está configurado (faltan PAGE_ID / PAGE_TOKEN)")
                    res["facebook"] = post_facebook(it).get("id")
                it["status"], it["results"], it["published_at"] = "published", res, now.isoformat()
                it.pop("error", None)
            except Exception as e:
                it["attempts"] = it.get("attempts", 0) + 1
                it["error"] = str(e)[:500]
                if it["attempts"] >= MAX_ATTEMPTS:
                    it["status"] = "error"
                print("   ✗", it["error"])
            changed = True
        if changed and not DRY:
            json.dump(week, open(fp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("listo" + (" (dry-run)" if DRY else ""))


if __name__ == "__main__":
    main()
