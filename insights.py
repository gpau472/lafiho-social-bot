#!/usr/bin/env python3
"""Informe semanal: qué funcionó en Instagram y Facebook (gratis, API oficial de Meta).
Genera reports/AAAA-Www.json y reports/AAAA-Www.md  ·  Variables: PAGE_TOKEN, IG_USER_ID, PAGE_ID
"""
import os, json, sys
from datetime import datetime, timezone, timedelta
import requests

GRAPH = "https://graph.facebook.com/v21.0"
TOKEN, IG, PAGE = os.environ.get("PAGE_TOKEN", ""), os.environ.get("IG_USER_ID", ""), os.environ.get("PAGE_ID", "")
DAYS = int(os.environ.get("DAYS", "14"))


def get(path, **params):
    params["access_token"] = TOKEN
    r = requests.get(f"{GRAPH}/{path}", params=params, timeout=60)
    d = r.json()
    if r.status_code >= 400 or "error" in d:
        return {"_error": d.get("error", d)}
    return d


def main():
    since = datetime.now(timezone.utc) - timedelta(days=DAYS)
    acct = get(IG, fields="username,followers_count,follows_count,media_count")
    media = get(f"{IG}/media", fields="id,caption,media_type,media_product_type,timestamp,permalink,like_count,comments_count", limit=50)
    rows = []
    for m in media.get("data", []):
        ts = datetime.fromisoformat(m["timestamp"].replace("+0000", "+00:00"))
        if ts < since:
            continue
        ins = get(f"{m['id']}/insights", metric="reach,saved,shares,total_interactions")
        vals = {x["name"]: x["values"][0]["value"] for x in ins.get("data", [])} if "data" in ins else {}
        reach = vals.get("reach", 0)
        inter = vals.get("total_interactions", (m.get("like_count", 0) + m.get("comments_count", 0)))
        rows.append({
            "id": m["id"], "tipo": m.get("media_product_type") or m.get("media_type"), "fecha": m["timestamp"][:10],
            "enlace": m.get("permalink"), "texto": (m.get("caption") or "")[:90].replace("\n", " "),
            "likes": m.get("like_count", 0), "comentarios": m.get("comments_count", 0),
            "guardados": vals.get("saved", 0), "compartidos": vals.get("shares", 0), "alcance": reach,
            "interacciones": inter, "tasa_interaccion": round(inter / reach, 4) if reach else None,
        })
    fb = get(f"{PAGE}/posts", fields="message,created_time,reactions.summary(true),comments.summary(true),shares", limit=20) if PAGE else {}
    week = datetime.now(timezone.utc).strftime("%G-W%V")
    out = {"semana": week, "cuenta": acct, "publicaciones": rows, "facebook": fb.get("data", [])}
    os.makedirs("reports", exist_ok=True)
    json.dump(out, open(f"reports/{week}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    best = sorted([r for r in rows if r["alcance"]], key=lambda r: (r["tasa_interaccion"] or 0), reverse=True)
    by_type = {}
    for r in rows:
        by_type.setdefault(r["tipo"], []).append(r)
    md = [f"# Informe {week}", "", f"Seguidores: **{acct.get('followers_count','?')}** · publicaciones totales: {acct.get('media_count','?')}", ""]
    md += ["## Top por tasa de interacción", "", "| Fecha | Tipo | Alcance | Interacc. | Tasa | Guardados | Compart. | Texto |", "|---|---|---|---|---|---|---|---|"]
    for r in best[:8]:
        md.append(f"| {r['fecha']} | {r['tipo']} | {r['alcance']} | {r['interacciones']} | {r['tasa_interaccion']} | {r['guardados']} | {r['compartidos']} | {r['texto']} |")
    md += ["", "## Media por formato", "", "| Formato | Nº | Alcance medio | Interacc. media |", "|---|---|---|---|"]
    for t, rs in by_type.items():
        n = len(rs)
        md.append(f"| {t} | {n} | {sum(x['alcance'] for x in rs)//n} | {sum(x['interacciones'] for x in rs)//n} |")
    open(f"reports/{week}.md", "w", encoding="utf-8").write("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
