# Resumen del Proyecto: Asset Foundry

Este documento resume todos los procedimientos, configuraciones y desarrollos realizados hasta la fecha en el proyecto **Asset Foundry**.

## 1. Pipeline de Datos y Generación de Datasets
Se ha implementado un sistema automatizado para la generación y gestión de datos sintéticos:
- **Scripts de Generación:** Dentro del directorio `modules/`, se han creado scripts en Python (`generar_csv_libros.py`, `generar_csv_usuarios.py`, `generar_csv_ventas.py` y `generar_libro.py`) encargados de poblar las bases de datos. Esto incluye la lógica especializada para la generación y venta de libros premium tipo "CB" (Chatbot).
- **Almacenamiento Consistente:** Todos los datos generados se consolidan en la carpeta `databases_asset_foundry/` en formato CSV (`dataset_libros_asset_foundry.csv`, `dataset_usuarios_asset_foundry.csv`, `dataset_ventas_asset_foundry.csv`).
- **Empaquetado (Zipping) para Machine Learning:** Se automatizó el proceso para comprimir todos estos datasets en un solo archivo `dataset_asset_foundry.zip`. Este archivo es consumido directamente por los modelos de machine learning que alimentan el panel administrativo.

## 2. Dashboard Administrativo
- **Módulo Principal:** Se desarrolló `modules/dashboard.py`, un panel de administración en Python diseñado para consumir el `dataset_asset_foundry.zip` y presentar análisis de datos, reportes y métricas accionadas por modelos predictivos/ML.

## 3. Automatización de Entorno y Despliegue Local
Para evitar conflictos de dependencias y simplificar el inicio del ecosistema, se implementaron rutinas de automatización mediante scripts Batch:
- **Instalación (`instalar_dashboard.bat`):** Un script que crea automáticamente un entorno virtual de Python (`asset_foundry_env`) e instala las librerías necesarias especificadas en `modules/requisitos.txt`.
- **Ejecución y Gestión de Red (`Iniciar_Fabrica.bat`):** Es el orquestador principal. No solo levanta el dashboard usando su entorno virtual aislado, sino que también resuelve un problema crítico con los límites de **ngrok** (que en cuentas gratuitas solo permite un endpoint). Para ello, configura el servicio de webhooks (n8n) conectándolo a un *Cloud Endpoint estático* de ngrok para que permanezca confiable, permitiendo simultáneamente que el dashboard opere en local sin conflictos de túneles.

## 4. Estructura Principal del Repositorio
- `index.html`: Página principal de la interfaz web (frontend).
- `Iniciar_Fabrica.bat` / `instalar_dashboard.bat`: Controladores de ejecución y preparación del entorno.
- `asset_foundry_env/`: Entorno virtual de Python exclusivo.
- `databases_asset_foundry/` y `dataset_asset_foundry.zip`: Bases de datos crudas y empaquetadas.
- `modules/`: Código fuente principal (generadores, dashboard y dependencias).

## 5. Historial de Actualizaciones (Update Logger)

**[23 de Abril de 2026] - Interconexión de Interfaces**
- **Frontend (`index.html`):** Se actualizó el botón "Dashboard" del menú de navegación para enlazar directamente al puerto local donde se levanta Streamlit (`http://localhost:8501`), mejorando la transición entre la tienda y el panel de administración.
- **Dashboard (`modules/dashboard.py`):** Se modificó la renderización del logotipo en la barra lateral. Ahora la imagen se procesa en Base64 y se renderiza mediante código HTML integrado en Streamlit (`st.markdown`), permitiendo que el logo funcione como un hipervínculo de retorno al frontend (`http://127.0.0.1:5500/index.html`).

**[23 de Abril de 2026] - Dockerización y Proxy Inverso**
- **Contenedorización Total:** Se migró todo el ecosistema (Flask, Streamlit, n8n) a una arquitectura basada en Docker utilizando `docker-compose.yml`. Todos los servicios ahora corren aislados y se comunican a través de una red interna de Docker.
- **Proxy Inverso con Nginx:** Se introdujo Nginx (`nginx.conf`) para actuar como recepcionista del tráfico. Nginx expone el puerto 80 y enruta dinámicamente las peticiones basándose en la URL:
  - `/` sirve estáticamente el frontend (`index.html`).
  - `/dashboard/` redirige al contenedor de Streamlit.
  - `/webhook/` redirige a n8n.
  - `/api/` redirige a Flask.
- **Resolución de Límites de Ngrok:** Se optimizó `Iniciar_Fabrica.bat` para levantar Docker Compose y posteriormente lanzar un único túnel de Ngrok (`ngrok http 80 --url https://default.internal`) conectado a Nginx. Esto soluciona la limitación de cuentas gratuitas de Ngrok (1 dominio máximo) permitiendo exponer múltiples servicios bajo el mismo dominio estático de la nube.
- **Ajustes de Código:** Se actualizó `generar_libro.py` para escuchar en `0.0.0.0` y los enlaces internos de `dashboard.py` e `index.html` para usar rutas relativas soportadas por el proxy.

**[23 de Abril de 2026] - Botón de Workflows y Refactorización de n8n**
- **Frontend (`index.html`):** Se integró un botón "Workflows" en la barra de navegación configurado para redirigir al panel de n8n a través del nuevo endpoint `/workflows/`. Se mantuvo la lógica CSS para que solo sea visible para el rol Administrativo. Además, se actualizó la ruta del Chatbot interno (`webhookUrl`) para que envíe sus peticiones al nuevo endpoint.
- **Proxy y Contenedorización:** Se reconfiguró `nginx.conf` y `docker-compose.yml` para soportar n8n bajo la sub-ruta `/workflows/`.
  - Se añadieron las variables de entorno `N8N_PATH`, `N8N_EDITOR_BASE_URL` y `N8N_PROXY_HOPS` en Docker.
  - En Nginx, se incluyeron directivas críticas para WebSockets (`proxy_buffering off`, `chunked_transfer_encoding off`, `proxy_cache off`) asegurando que la interfaz de usuario de n8n no se quede en blanco ni pierda la conexión (Server-Sent Events) con su backend interno.

**[23 de Abril de 2026] - Aumento de Timeout en Nginx**
- **Nginx (`nginx.conf`):** Se aumentaron los límites de tiempo de espera (`proxy_read_timeout`, `proxy_connect_timeout` y `proxy_send_timeout`) a 86400 segundos (24 horas) en la ruta `/workflows/`. Esto soluciona dos problemas críticos: el error "504 Gateway Time-out" del Chatbot de IA, y las desconexiones periódicas (cada pocos minutos) de la interfaz de edición de n8n, la cual depende de conexiones persistentes (Server-Sent Events) para mantener la sesión abierta sin interrupciones.
**[24 de Abril de 2026] - Restauración de Configuración n8n**
- Tras una intervención de optimización automática por parte de la IA de Docker, se borró el bloque de proxy de n8n y sus variables de entorno. Se procedió a restaurar el bloque `location /workflows/` en `nginx.conf` con sus políticas de WebSockets y timeouts de 24h, además de reinyectar `N8N_PATH`, `N8N_EDITOR_BASE_URL` y `N8N_PROXY_HOPS` en el `docker-compose.yml`.
- Se añadieron redirecciones estrictas (`location = /dashboard` y `location = /workflows`) en Nginx para corregir el problema de "This is your new Cloud Endpoint" al acceder sin barra final.
- **Dockerfile y .dockerignore:** La IA de Docker había excluido la carpeta `assets/` del contexto de build, provocando un `FileNotFoundError` al cargar `Logotipo.png` en el dashboard de Streamlit. Se eliminó `assets/` de `.dockerignore` y se añadió `COPY assets/ ./assets/` al `Dockerfile`.
- **Instalación limpia de n8n:** Se eliminó el volumen persistente `n8n_data`, se descargó la última imagen (`docker.n8n.io/n8nio/n8n:latest`) y se recreó el contenedor desde cero para resolver problemas de autenticación. El editor es accesible en `/workflows/`.
- **URLs absolutas para OAuth:** Se actualizó `N8N_EDITOR_BASE_URL` y se añadió `WEBHOOK_URL` con el dominio completo de Ngrok (`https://funnelform-mirta-incomparably.ngrok-free.dev/workflows/`) en `docker-compose.yml`. Esto corrige que las URLs de callback de OAuth2 aparecieran sin dominio, impidiendo la creación de credenciales de Google.

**[25 de Abril de 2026] - Diapositiva de Video en el Hero**
- **Frontend (`index.html`):** Se añadió una nueva primera diapositiva al carrusel del hero que integra el video `assets/video.mp4` en un reproductor custom con controles de play/pausa, barra de progreso, indicador de tiempo y botón de silenciar/activar audio.
- **Diseño:** La diapositiva muestra el título "Esto es Asset Foundry" y el reproductor ocupa la mayor parte del área del hero con un diseño premium (bordes redondeados, sombra profunda, controles con glassmorphism).
- **Lógica de avance:** La diapositiva del video no usa temporizador fijo; avanza automáticamente a la siguiente escena solo cuando el video termina de reproducirse (evento `ended`). Si el autoplay es bloqueado por el navegador, el video se inicia silenciado automáticamente.
- **Reestructuración:** Las 6 escenas originales (1-6) se renumeraron a 2-7 para acomodar la nueva escena de video como escena 1. Se añadió una séptima barra de progreso y se actualizó el contador de escenas.

**[25 de Abril de 2026] - Botón "Generar Libro" en el Dashboard**
- **Dashboard (`modules/dashboard.py`):** Se añadió un botón "📕 Generar Libro" en la barra lateral, debajo de la sección de generación de dataset. Al pulsarlo, envía una petición POST al webhook de n8n (`/workflows/webhook/b473481c-...`) con un timeout de 120 segundos.
- **Consola de respuesta:** Justo debajo del botón se muestra una mini-consola estilizada (fondo oscuro, fuente monoespaciada) que presenta el código de estado HTTP y el cuerpo de la respuesta del webhook. El status se colorea en verde (200) o rojo (error).
- **Dependencia:** Se añadió `import requests` al módulo.

**[25 de Abril de 2026] - Preparación para Despliegue en Producción 24/7**
- **Análisis de Compatibilidad con Wasmer.io:** Se realizó un análisis exhaustivo del proyecto completo (4 servicios Docker: Nginx, Flask, Streamlit, n8n) contra los requisitos de Wasmer Edge. Se determinó que Wasmer es **incompatible** con la arquitectura actual debido a: (1) n8n no compila a WebAssembly, (2) extensiones C nativas de Python (scikit-learn, numpy, matplotlib, reportlab) sin soporte WASM, (3) arquitectura multi-servicio sin equivalente en Wasmer, (4) necesidad de estado persistente (SQLite de n8n, CSVs). Se seleccionó **Railway.app** como plataforma de hosting alternativa.
- **[NUEVO] `docker-compose.production.yml`:** Versión del Compose para producción que elimina la dependencia de Ngrok. Las URLs de n8n (`N8N_EDITOR_BASE_URL`, `WEBHOOK_URL`) ahora usan la variable de entorno `${DOMAIN}` en lugar de un dominio Ngrok hardcodeado. El puerto de n8n ya no se expone directamente (solo a través de Nginx).
- **[NUEVO] `nginx.production.conf`:** Configuración de Nginx para producción con headers de seguridad añadidos (`X-Frame-Options`, `X-Content-Type-Options`, `X-XSS-Protection`, `Referrer-Policy`) y políticas de caché separadas para video.
- **[NUEVO] `railway.toml`:** Archivo de configuración para el despliegue automático en Railway.app.
- **[NUEVO] `.env.example`:** Template de variables de entorno para producción (`DOMAIN`, `PORT`).
- **[NUEVO] `DEPLOY.md`:** Guía paso a paso para desplegar en Railway.app o VPS.
- **Eliminación de URLs Hardcodeadas de Ngrok:**
  - **`index.html`:** La `webhookUrl` del chat de n8n (Archie) ahora usa `window.location.origin` + ruta relativa, haciéndola funcionar en cualquier dominio automáticamente.
  - **`dashboard.py`:** La URL del webhook de generación de libros ahora se construye dinámicamente desde la variable de entorno `BASE_DOMAIN`, con detección automática de protocolo (HTTP/HTTPS).
- **Nota:** El `docker-compose.yml` original y `nginx.conf` se mantienen sin cambios para preservar la compatibilidad con el entorno de desarrollo local con Ngrok.

**[25 de Abril de 2026] - Corrección de Error 404 en Railway (Despliegue Multi-servicio)**
- **Arquitectura:** Se eliminó `railway.toml`, que estaba forzando un despliegue de un solo servicio (Flask), impidiendo que Nginx, el Dashboard y n8n se iniciaran. Al eliminarlo, Railway ahora detecta correctamente el ecosistema completo mediante `docker-compose.yml`.
- **Nginx de Producción:**
  - Se creó `Dockerfile.nginx` para empaquetar la configuración y los archivos estáticos dentro de la imagen. Esto es necesario en Railway ya que no se pueden montar carpetas del repositorio en tiempo de ejecución.
- **Red Interna y DNS:** Se actualizaron los upstreams en `nginx.production.conf` al formato `<servicio>.railway.internal` para cumplir con los requisitos de red privada de Railway. Además, se fijaron los puertos internos de Flask (9000), Dashboard (8501) y n8n (5678) en el `docker-compose.yml` para evitar conflictos con el puerto dinámico asignado por Railway al proxy principal.
- **Resultado:** Nginx ahora puede localizar correctamente los servicios internos, y el tráfico se dirige al contenedor correcto siempre que el dominio esté vinculado al servicio `nginx` en el panel de Railway.

