#!/usr/bin/env python3
"""Muestra tu IG_USER_ID a partir del token de Instagram (ejecútalo TÚ; el token no se comparte).
   IG_TOKEN=xxxx python3 get_ig_id.py
"""
import os, sys, requests
t = os.environ.get("IG_TOKEN") or sys.exit("Falta IG_TOKEN")
d = requests.get("https://graph.instagram.com/v21.0/me", params={"fields": "user_id,username,account_type,followers_count", "access_token": t}, timeout=30).json()
print(d)
if "user_id" in d or "id" in d:
    print("\nIG_USER_ID =", d.get("user_id") or d.get("id"))
