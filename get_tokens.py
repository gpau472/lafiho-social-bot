#!/usr/bin/env python3
"""Convierte el token corto del Explorador de la API Graph en el PAGE_TOKEN permanente
y localiza PAGE_ID e IG_USER_ID.  Ejecútalo TÚ en tu Mac (los tokens no se comparten con nadie).

  APP_ID=... APP_SECRET=... SHORT_TOKEN=... python get_tokens.py
"""
import os, sys, requests
G = "https://graph.facebook.com/v21.0"
app, sec, short = os.environ.get("APP_ID"), os.environ.get("APP_SECRET"), os.environ.get("SHORT_TOKEN")
if not (app and sec and short):
    sys.exit("Faltan APP_ID, APP_SECRET o SHORT_TOKEN")
ll = requests.get(f"{G}/oauth/access_token", params={"grant_type": "fb_exchange_token", "client_id": app, "client_secret": sec, "fb_exchange_token": short}).json()
if "access_token" not in ll:
    sys.exit(f"Error al alargar el token: {ll}")
pages = requests.get(f"{G}/me/accounts", params={"access_token": ll["access_token"], "fields": "id,name,access_token,instagram_business_account"}).json()
for p in pages.get("data", []):
    ig = (p.get("instagram_business_account") or {}).get("id")
    print("-" * 60)
    print("Página:", p["name"])
    print("PAGE_ID     =", p["id"])
    print("IG_USER_ID  =", ig or "(esta página no tiene Instagram profesional enlazado)")
    print("PAGE_TOKEN  =", p["access_token"])
print("-" * 60)
print("Copia PAGE_ID, IG_USER_ID y PAGE_TOKEN a GitHub > Settings > Secrets and variables > Actions.")
