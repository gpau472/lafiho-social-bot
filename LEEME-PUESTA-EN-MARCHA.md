# LAFIHO · Bot de redes sociales (coste 0 €)

Publica en **Instagram y Facebook** lo que tú apruebes, a la hora programada, y genera un **informe semanal**.
Todo con herramientas gratuitas: API oficial de Meta + GitHub (repositorio y Actions) + mi producción local.
**Nada se publica sin tu OK** (cada pieza tiene `"approved": false` hasta que tú me lo confirmes).

## ▶ CAMINO A · SOLO INSTAGRAM (sin Facebook, sin página, sin tocar tu perfil personal)
Usa la API oficial **con inicio de sesión de Instagram**. Secrets necesarios: `IG_TOKEN` y `IG_USER_ID` (nada de PAGE_*).

1. **Instagram → cuenta profesional** (Empresa o Creador): app de Instagram → Configuración y actividad → Tipo de cuenta y herramientas → *Cambiar a cuenta profesional*.
2. **Cuenta de desarrollador de Meta (gratis):** entra en developers.facebook.com con la sesión de Facebook que tengas abierta y acepta ser desarrollador.
   *(Meta lo pide una vez. Si te exige una contraseña que no recuerdas, este es el único punto de bloqueo: dímelo y vemos la alternativa.)*
3. **Crear app:** *Mis apps → Crear app* → tipo **Empresa**. Dentro, añade el producto **Instagram** → *API con inicio de sesión de Instagram*.
4. **Añadirte como probador:** en la app → *Roles de la app → Roles* → **Probadores de Instagram** → añade tu usuario de Instagram. Luego, en Instagram (web) → *Configuración → Apps y sitios web → Invitaciones de probador* → **Aceptar**.
5. **Token:** en la app → Instagram → *Configuración de la API con inicio de sesión de Instagram* → **Generar token** junto a tu cuenta → cópialo (no lo compartas).
6. **Tu ID:** `IG_TOKEN=xxxx python3 get_ig_id.py` → imprime `IG_USER_ID`.
7. **GitHub → Settings → Secrets and variables → Actions → New repository secret:** crea **IG_TOKEN** e **IG_USER_ID**.
8. **Caduca a los 60 días:** repite los pasos 5-7 cada ~50 días (te aviso en el informe del sábado).
9. **Prueba segura:** una publicación de prueba aprobada por ti; se publica y la borras.

> Los pasos del *Camino B* de abajo (Facebook + página) quedan para más adelante, cuando recuperes ese acceso.

---

## Piezas
| Archivo | Para qué |
|---|---|
| `publisher.py` | Cada 15 min (GitHub Actions) publica lo **aprobado y vencido**: post, carrusel, reel, historia → IG y espejo en Facebook |
| `insights.py` | Cada sábado genera `reports/AAAA-Www.md` con lo que mejor ha funcionado |
| `get_tokens.py` | Te da `PAGE_ID`, `IG_USER_ID` y `PAGE_TOKEN` (permanente) a partir del token del Explorador |
| `schedule/` | Una semana = un JSON con piezas, fecha/hora, texto y archivos |
| `media/` | Imágenes y vídeos de cada semana (`media/2026-W42/…`) |
| `reports/` | Informes semanales |
| `ejemplos/semana-ejemplo.json` | Formato de una semana |

## Puesta en marcha (una sola vez, ~30 min, lo haces tú)
**Importante:** los tokens y claves NO me los pases por el chat. Se pegan solo en GitHub (Secrets).

1. **Instagram profesional + página de Facebook enlazadas.**
   Instagram → Ajustes → Tipo de cuenta → *Cambiar a cuenta profesional* (empresa). Luego enlázala a tu página de Facebook (Ajustes → Cuenta vinculada).
2. **Cuenta gratuita de GitHub** (github.com) y crea un repositorio **público** llamado `lafiho-social-bot`.
   (Público para que Instagram pueda leer las imágenes; es gratis y sin límite de Actions.)
3. **App de Meta (gratis):** entra en developers.facebook.com → *Mis apps* → *Crear app* → tipo *Empresa*.
   Añade tu usuario como administrador (ya lo eres). En modo desarrollo **no hace falta revisión de Meta** para publicar en tus propias cuentas.
4. **Token:** *Herramientas → Explorador de la API Graph* → elige tu app → *Obtener token de usuario* con permisos:
   `pages_show_list, pages_read_engagement, pages_manage_posts, instagram_basic, instagram_content_publish, instagram_manage_insights, business_management`.
   Copia el token y ejecuta en tu Mac:
   ```bash
   cd lafiho-social-bot
   APP_ID=xxxx APP_SECRET=xxxx SHORT_TOKEN=xxxx python3 get_tokens.py
   ```
   Te imprime `PAGE_ID`, `IG_USER_ID` y `PAGE_TOKEN`.
5. En GitHub: repo → *Settings → Secrets and variables → Actions → New repository secret*: crea **PAGE_ID**, **IG_USER_ID**, **PAGE_TOKEN**.
6. Sube esta carpeta al repositorio (arrastrándola en la web de GitHub o con `git push`). Las acciones `Publicar lo aprobado` e `Informe semanal` se activan solas.
7. **Prueba:** una pieza de prueba aprobada con hora ya pasada y borra la publicación después, o pulsa *Run workflow* en la pestaña Actions.

## Ciclo semanal (fin de semana)
| Cuándo | Qué pasa |
|---|---|
| **Sábado mañana** | Sale solo el informe de la semana. Yo lo leo y propongo qué repetir/cambiar |
| **Sábado** | Tú me dices las **novedades**: funcionalidades nuevas, integraciones, ofertas, clientes, preguntas recibidas |
| **Sábado tarde** | Preparo la semana: 7 posts (uno al día), 2 reels, 3–4 historias, con textos y hashtags |
| **Domingo** | **Tú das el OK** (pieza a pieza o todo). Yo marco `approved:true` y subo a GitHub |
| **Lun–Dom** | El bot publica a la hora programada en Instagram y Facebook |

### Calendario tipo (se adapta a las novedades)
| Día | Post | Extra |
|---|---|---|
| Lun | Dato legal (RDL 8/2019) | Historia: mito |
| Mar | Funcionalidad (demo con captura real) | |
| Mié | Carrusel FAQ / educativo | **Reel 1** · Historia con encuesta (manual) |
| Jue | **Novedad / integración nueva** | |
| Vie | Mito vs realidad | Historia: demo |
| Sáb | Caso de uso / sector (hostelería, comercio, etc.) | |
| Dom | Oferta (2 meses gratis) / pregunta a la audiencia | **Reel 2** · Historia con pregunta (manual) |

### Tipos de contenido (para no repetirnos)
Funcionalidades · integraciones y novedades · ley / RDL 8/2019 · mitos y FAQ · casos por sector · antes/después · trucos de gestión de equipos · oferta · detrás de cámaras · respuestas a preguntas de seguidores.

## Límites que conviene saber
- **Pegatinas de historias** (encuesta, preguntas, enlace) y **música de Instagram**: no se pueden poner por API → esas historias llevan `"manual": true` y te las dejo listas para subir tú en 1 minuto.
- **Facebook:** se replican posts, carruseles y vídeos; las historias de Facebook no.
- **Comentarios y mensajes:** te preparo respuestas, **no respondo solo**.
- **Tokens:** el `PAGE_TOKEN` derivado de un token largo no caduca; si Meta lo invalida (cambio de contraseña, etc.) hay que repetir el paso 4.
- **Viralidad:** no se puede garantizar. Mido, pruebo ganchos y repito lo que funciona.
- **Datos legales:** solo afirmaciones verificadas, con el aviso *no es asesoramiento legal*.

## Si prefieres no usar la API
Alternativa 100 % gratis y sin código: **Meta Business Suite** (business.facebook.com). Yo te dejo la semana lista (`media/` + textos) y la programas tú en ~10 min. Es menos automático, pero no necesita tokens.
