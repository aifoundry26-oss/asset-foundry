# 🚀 Guía de Despliegue — Asset Foundry en Producción

## Requisitos Previos
- Cuenta en [Railway.app](https://railway.app) (o Render/VPS según tu elección)
- Repositorio Git (GitHub recomendado)

---

## Opción A: Despliegue en Railway.app (Recomendado)

### Paso 1: Subir a GitHub
```bash
cd "Website - Docker"
git init
git add .
git commit -m "Asset Foundry — Preparado para producción"
git remote add origin https://github.com/TU_USUARIO/asset-foundry.git
git push -u origin main
```

### Paso 2: Crear Proyecto en Railway
1. Ve a [railway.app/new](https://railway.app/new)
2. Selecciona **"Deploy from GitHub repo"**
3. Conecta tu repositorio `asset-foundry`
4. Railway detectará el `docker-compose.production.yml` automáticamente

### Paso 3: Configurar Variables de Entorno
En el panel de Railway → **Variables**, añade:

| Variable | Valor |
|---|---|
| `DOMAIN` | `tu-app.up.railway.app` (Railway te asigna uno automático) |
| `PORT` | `80` (Railway lo configura automáticamente) |

### Paso 4: Desplegar
- Haz clic en **Deploy** 
- Railway construirá los 4 contenedores automáticamente
- Tu sitio estará disponible en `https://tu-app.up.railway.app`

### Paso 5: Dominio Personalizado (Opcional)
1. En Railway → **Settings** → **Domains**
2. Añade tu dominio (ej: `assetfoundry.com`)
3. Configura un CNAME en tu proveedor DNS apuntando a Railway
4. Railway gestiona SSL automáticamente

---

## Opción B: Despliegue en VPS (DigitalOcean/Hetzner)

### Paso 1: Provisionar Servidor
```bash
# En el VPS (Ubuntu 22.04+)
sudo apt update && sudo apt upgrade -y
sudo apt install docker.io docker-compose-plugin git -y
sudo systemctl enable docker
```

### Paso 2: Clonar y Configurar
```bash
git clone https://github.com/TU_USUARIO/asset-foundry.git
cd asset-foundry
cp .env.example .env
nano .env   # Editar DOMAIN con tu dominio o IP pública
```

### Paso 3: Lanzar
```bash
docker compose -f docker-compose.production.yml up -d
```

### Paso 4: SSL con Certbot (si tienes dominio)
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d tu-dominio.com
```

---

## Estructura de Archivos de Producción

```
Website - Docker/
├── .env.example                      ← Template de variables de entorno
├── docker-compose.yml                ← Entorno LOCAL (con Ngrok)
├── docker-compose.production.yml     ← Entorno PRODUCCIÓN (Railway/VPS)
├── nginx.conf                        ← Nginx LOCAL
├── nginx.production.conf             ← Nginx PRODUCCIÓN (con headers de seguridad)
├── railway.toml                      ← Config específica de Railway
├── Dockerfile                        ← Sin cambios
└── ...
```

## ⚠️ Nota sobre el Video (100 MB)
El archivo `assets/video.mp4` pesa ~100 MB. Para mejorar tiempos de carga, se recomienda:
1. Subirlo a **YouTube** (como no listado) y usar un embed
2. Subirlo a **Google Drive** y usar enlace directo
3. Usar **Cloudflare R2** u otro CDN de objetos

Luego actualizar la referencia en `index.html` línea 381:
```html
<video id="hero-video" src="TU_URL_CDN" preload="auto" ...>
```
