import streamlit as st
import pandas as pd
import numpy as np
import zipfile
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import r2_score, mean_absolute_error, accuracy_score, precision_score
import os
import subprocess
import sys
import base64
import requests

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
logo_path = os.path.join(base_dir, "assets", "Logo.png")
logotipo_path = os.path.join(base_dir, "assets", "Logotipo.png")

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Asset Foundry - Core IA", page_icon=logo_path, layout="wide")

# --- VARIABLES DE ESTADO ---
if 'data_cargada' not in st.session_state:
    st.session_state.data_cargada = False
    st.session_state.datasets = {}

# --- FUNCIÓN MODAL PARA EDA ---
@st.dialog("📊 Exploración de Datos Crudos", width="large")
def modal_eda():
    st.markdown("Revisa las estructuras internas de la base de datos de Asset Foundry.")
    dataset_seleccionado = st.selectbox("Selecciona la tabla:", list(st.session_state.datasets.keys()))
    df_actual = st.session_state.datasets[dataset_seleccionado]
    
    col1, col2 = st.columns(2)
    col1.metric("Total Registros", df_actual.shape[0])
    col2.metric("Total Variables", df_actual.shape[1])
    
    st.dataframe(df_actual, use_container_width=True)
    st.write("Estadísticas Descriptivas:")
    st.write(df_actual.describe())

# ==========================================
# BARRA LATERAL (SIDEBAR)
# ==========================================
with st.sidebar:
    # Función local para convertir imagen a base64
    def get_image_as_base64(path):
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
            
    img_b64 = get_image_as_base64(logotipo_path)
    # Hacemos que el logo sea clickeable hacia la tienda (Nginx lo servirá en la ruta raíz /)
    st.markdown(
        f'<a href="/"><img src="data:image/png;base64,{img_b64}" width="100%" style="margin-bottom: 10px;"></a>',
        unsafe_allow_html=True
    )
    
    st.markdown("### Centro de Control IA")
    st.divider()
    
    # 1. Cargador de Archivos
    st.markdown("📦 **Carga de Datos**")
    
    def process_zip(zip_source):
        with zipfile.ZipFile(zip_source) as z:
            for nombre_archivo in z.namelist():
                if nombre_archivo.endswith('.csv'):
                    with z.open(nombre_archivo) as f:
                        df = pd.read_csv(f)
                        # Conversión de fechas automática si existen
                        for col in df.columns:
                            if 'fecha' in col.lower():
                                df[col] = pd.to_datetime(df[col], errors='coerce')
                        
                        if 'libro' in nombre_archivo.lower():
                            st.session_state.datasets['libros'] = df
                        elif 'usuario' in nombre_archivo.lower():
                            st.session_state.datasets['usuarios'] = df
                        elif 'venta' in nombre_archivo.lower():
                            st.session_state.datasets['ventas'] = df
        st.session_state.data_cargada = True
        st.rerun()

    if not st.session_state.data_cargada:
        uploaded_zip = st.file_uploader("Sube el archivo .zip", type="zip")
        if uploaded_zip is not None:
            process_zip(uploaded_zip)
            
        st.markdown("---")
        st.markdown("⚡ **Generación Automática**")
        if st.button("Generar Dataset", use_container_width=True):
            with st.spinner("Ejecutando motores de datos (esto puede tardar unos segundos)..."):
                script_libros = os.path.join(base_dir, "modules", "generar_csv_libros.py")
                script_usuarios = os.path.join(base_dir, "modules", "generar_csv_usuarios.py")
                script_ventas = os.path.join(base_dir, "modules", "generar_csv_ventas.py")
                
                # Ejecutar scripts en orden
                subprocess.run([sys.executable, script_libros], check=True)
                subprocess.run([sys.executable, script_usuarios], check=True)
                subprocess.run([sys.executable, script_ventas], check=True)
                
                # Cargar el ZIP generado automáticamente
                zip_generado = os.path.join(base_dir, "dataset_asset_foundry.zip")
                if os.path.exists(zip_generado):
                    process_zip(zip_generado)
                else:
                    st.error("Hubo un error al ubicar el archivo ZIP generado.")

    st.markdown("---")
    st.markdown("📖 **Generación de Libros**")
    if st.button("📕 Generar Libro", use_container_width=True):
        with st.spinner("Contactando al sistema de generación…"):
            try:
                # URL relativa: Nginx enruta /workflows/ internamente a n8n.
                # Funciona igual en local (Docker) y en producción (Railway/VPS).
                import os
                base_domain = os.environ.get("BASE_DOMAIN", "localhost")
                protocol = "https" if base_domain != "localhost" else "http"
                webhook_url = f"{protocol}://{base_domain}/workflows/webhook/b473481c-920c-426f-bebf-34b14281a5f5"
                resp = requests.post(
                    webhook_url,
                    json={},
                    timeout=120
                )
                st.session_state.libro_response = resp.text
                st.session_state.libro_status = resp.status_code
            except Exception as e:
                st.session_state.libro_response = str(e)
                st.session_state.libro_status = "Error"

    if 'libro_response' in st.session_state:
        status = st.session_state.libro_status
        color = "#10B981" if status == 200 else "#EF4444"
        st.markdown(
            f'<div style="background:#1a1a2e;border-radius:8px;padding:10px 14px;margin-top:6px;'
            f'font-family:monospace;font-size:0.75rem;color:#d1d5db;max-height:200px;overflow-y:auto;'
            f'border:1px solid #2d2d4a;">'
            f'<span style="color:{color};font-weight:700;">Status: {status}</span><br>'
            f'<pre style="white-space:pre-wrap;word-break:break-all;margin:6px 0 0;color:#e2e8f0;">{st.session_state.libro_response}</pre>'
            f'</div>',
            unsafe_allow_html=True
        )

    if st.session_state.data_cargada:
        st.success("✅ Base de datos activa")
        
        # Botón para abrir el Modal de Exploración
        if st.button("🔍 Abrir Explorador de Datos (EDA)", use_container_width=True):
            modal_eda()
            
        st.divider()
        
        # 2. Filtro de Fechas Global
        st.markdown("📅 **Filtro Temporal**")
        df_ventas_base = st.session_state.datasets.get('ventas')
        if df_ventas_base is not None and 'Fecha' in df_ventas_base.columns:
            min_date = df_ventas_base['Fecha'].min().date()
            max_date = df_ventas_base['Fecha'].max().date()
            
            fechas_seleccionadas = st.date_input("Selecciona el rango:", value=(min_date, max_date), min_value=min_date, max_value=max_date)
            
            if len(fechas_seleccionadas) == 2:
                fecha_inicio, fecha_fin = fechas_seleccionadas
            else:
                fecha_inicio, fecha_fin = min_date, max_date
        else:
            fecha_inicio, fecha_fin = None, None

# ==========================================
# PÁGINA PRINCIPAL - KPIS Y GRÁFICOS
# ==========================================
if not st.session_state.data_cargada:
    st.info("👈 Por favor, despliega la barra lateral e ingresa el archivo .zip con los datos generados para comenzar.")
else:
    # --- PROCESAMIENTO DE FILTROS TEMPORALES ---
    df_v = st.session_state.datasets['ventas'].copy()
    df_l = st.session_state.datasets['libros'].copy()
    df_u = st.session_state.datasets['usuarios'].copy()
    
    if fecha_inicio and fecha_fin:
        mask_v = (df_v['Fecha'].dt.date >= fecha_inicio) & (df_v['Fecha'].dt.date <= fecha_fin)
        df_v_filtrado = df_v.loc[mask_v]
    else:
        df_v_filtrado = df_v
        
    # --- CÁLCULO DE KPIs GLOBALES (Siempre visibles) ---
    ventas_exitosas = df_v_filtrado[df_v_filtrado['Compro'] == 1]
    ventas_con_precio = ventas_exitosas.merge(df_l[['ID_Libro', 'Precio_Venta']], on='ID_Libro', how='left')
    ingresos_totales = ventas_con_precio['Precio_Venta'].sum()
    tasa_conversion = (len(ventas_exitosas) / len(df_v_filtrado)) * 100 if len(df_v_filtrado) > 0 else 0
    
    st.markdown("### 📈 Rendimiento General")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Ingresos Generados", f"${ingresos_totales:,.2f}")
    kpi2.metric("Tasa de Conversión", f"{tasa_conversion:.1f}%")
    kpi3.metric("Oportunidades (Interacciones)", len(df_v_filtrado))
    kpi4.metric("Libros en Catálogo", len(df_l))
    
    st.divider()
    
    # ==========================================
    # PESTAÑAS DE HERRAMIENTAS Y DASHBOARD
    # ==========================================
    tab_dashboard, tab1, tab2, tab3 = st.tabs([
        "🏠 Dashboard Principal",
        "💰 Calculadora de Precio (Regresión)", 
        "🎯 Probabilidad de Venta (Clasificación)", 
        "👥 Buyer Personas (Clustering PCA)"
    ])
    
    # --- TAB 0: DASHBOARD PRINCIPAL (NUEVO) ---
    with tab_dashboard:
        if df_v_filtrado.empty:
            st.warning("No hay datos disponibles para el rango de fechas seleccionado.")
        else:
            # Consolidar datos para el análisis
            df_insights = df_v_filtrado.merge(df_l, on='ID_Libro', how='left').merge(df_u, on='ID_Usuario', how='left')
            df_insights['Es_Premium'] = df_insights['ID_Libro'].astype(str).str.startswith('CB')
            
            # FILA 1: GRÁFICOS PRINCIPALES
            col_g1, col_g2 = st.columns(2)
            
            with col_g1:
                st.markdown("**📊 Evolución de Ventas en el Tiempo**")
                ventas_por_dia = df_v_filtrado.groupby(df_v_filtrado['Fecha'].dt.date)['Compro'].sum().reset_index()
                fig_line, ax_line = plt.subplots(figsize=(6, 3))
                sns.lineplot(data=ventas_por_dia, x='Fecha', y='Compro', marker='o', color='#00a4d3', ax=ax_line)
                ax_line.set_ylabel("Libros Vendidos")
                ax_line.set_xlabel("")
                plt.xticks(rotation=45)
                st.pyplot(fig_line)
                
            with col_g2:
                st.markdown("**📑 Rendimiento por Tema Principal**")
                ventas_tema = df_insights[df_insights['Compro'] == 1]['Tema_Principal'].value_counts().reset_index()
                fig_bar, ax_bar = plt.subplots(figsize=(6, 3))
                sns.barplot(data=ventas_tema, x='count', y='Tema_Principal', palette='viridis', ax=ax_bar)
                ax_bar.set_xlabel("Unidades Vendidas")
                ax_bar.set_ylabel("")
                st.pyplot(fig_bar)
            
            st.divider()
            
            # FILA 2: INTELIGENCIA OPERATIVA (RESÚMENES Y ALERTAS)
            st.markdown("### 🧠 Inteligencia Operativa (Alertas Automáticas)")
            col_ia1, col_ia2 = st.columns(2)
            
            with col_ia1:
                st.markdown("#### 💡 Insights de Negocio")
                
                # Insight 1: Mejor tema
                if not ventas_tema.empty:
                    mejor_tema = ventas_tema.iloc[0]['Tema_Principal']
                    porcentaje_mejor = (ventas_tema.iloc[0]['count'] / ventas_tema['count'].sum()) * 100
                    st.success(f"**Estrella del Catálogo:** El tema **{mejor_tema}** representa el **{porcentaje_mejor:.1f}%** de las ventas. La IA recomienda priorizar la creación de libros en esta categoría.")
                
                # Insight 2: Impacto Premium
                ventas_premium = df_insights[(df_insights['Compro'] == 1) & (df_insights['Es_Premium'] == True)]
                ingresos_premium = ventas_premium['Precio_Venta'].sum() if not ventas_premium.empty else 0
                if ingresos_totales > 0:
                    pct_premium = (ingresos_premium / ingresos_totales) * 100
                    st.info(f"**Línea Premium:** Los libros personalizados (Chatbot) están generando el **{pct_premium:.1f}%** de los ingresos totales facturados en este periodo.")

            with col_ia2:
                st.markdown("#### ⚠️ Advertencias y Cuellos de Botella")
                
                # Warning 1: Conversión general
                if tasa_conversion < 15.0:
                    st.warning(f"**Alerta de Conversión:** La tasa de conversión está en **{tasa_conversion:.1f}%**, por debajo del umbral óptimo (15%). Revisa la efectividad de los correos de retargeting o los prompts de Archie.")
                else:
                    st.success(f"**Conversión Saludable:** El flujo de ventas mantiene un ritmo excelente con un **{tasa_conversion:.1f}%** de cierre.")
                
                # Warning 2: Interacciones sin compra en usuarios estresados
                altos_estres_sin_compra = df_insights[(df_insights['Nivel_Estres_Declarado'] >= 8) & (df_insights['Compro'] == 0)]
                if not altos_estres_sin_compra.empty:
                    st.error(f"**Fuga de Usuarios Críticos:** Se detectaron **{len(altos_estres_sin_compra)}** interacciones de usuarios con niveles de estrés graves (8-10) que abandonaron sin comprar. Se sugiere implementar un descuento de rescate urgente para este segmento.")

    # --- TAB 1: REGRESIÓN LINEAL ---
    with tab1:
        st.subheader("Simulador de Precio Óptimo (Catálogo)")
        st.markdown("El modelo ajusta automáticamente el sesgo de los libros Premium (CB) para aprender patrones puros.")
        
        df_l_train = df_l.copy()
        mascara_premium = df_l_train['ID_Libro'].astype(str).str.startswith('CB', na=False)
        df_l_train.loc[mascara_premium, 'Precio_Venta'] -= 3.0 # Restar el valor base premium
        
        col_afap = 'Herramientas_AFAP' if 'Herramientas_AFAP' in df_l_train.columns else 'Tiene_Checklist_AFAP'
        X_reg = df_l_train[['Paginas', 'Nivel_Tendencia_Mercado', col_afap]]
        X_categorias = pd.get_dummies(df_l_train['Tema_Principal'], drop_first=True)
        X_reg = pd.concat([X_reg, X_categorias], axis=1)
        y_reg = df_l_train['Precio_Venta']
        
        mod_regresion = LinearRegression()
        mod_regresion.fit(X_reg, y_reg)
        
        with st.form("form_precio"):
            col_a, col_b, col_c = st.columns(3)
            with col_a: paginas = st.number_input("Páginas", 50, 100, 60)
            with col_b: tendencia = st.slider("Tendencia (1-10)", 1.0, 10.0, 7.5)
            with col_c: afap = st.slider("Cant. AFAP", 0, 5, 3)
            
            tema = st.selectbox("Tema Principal", df_l['Tema_Principal'].unique())
            btn_precio = st.form_submit_button("Calcular Precio")
            
            if btn_precio:
                input_data = pd.DataFrame(columns=X_reg.columns)
                input_data.loc[0] = 0 
                input_data['Paginas'] = paginas
                input_data['Nivel_Tendencia_Mercado'] = tendencia
                input_data[col_afap] = afap
                if f"Tema_Principal_{tema}" in input_data.columns:
                    input_data[f"Tema_Principal_{tema}"] = 1
                    
                precio_pred = mod_regresion.predict(input_data)[0]
                st.success(f"🏷️ **Precio sugerido para catálogo estándar:** ${precio_pred:.2f} USD")
                
    # --- TAB 2: CLASIFICACIÓN ---
    with tab2:
        st.subheader("Predictor de Conversión por Usuario")
        
        df_master = df_v_filtrado.merge(df_u, on='ID_Usuario', how='left').merge(df_l, on='ID_Libro', how='left')
        df_master['Coincide_Tema'] = (df_master['Tema_Frecuente'] == df_master['Tema_Principal']).astype(int)
        df_master['Es_Premium'] = df_master['ID_Libro'].astype(str).str.startswith('CB').astype(int)
        
        features_clf = ['Edad', 'Nivel_Estres_Declarado', 'Interacciones_Chatbot', 
                        'Sentimiento_NLP', 'Nivel_Tendencia_Mercado', 'Descuento_Ofrecido', 'Coincide_Tema', 'Es_Premium']
        
        X_clf = df_master[features_clf].fillna(0)
        y_clf = df_master['Compro']
        
        clf_modelo = RandomForestClassifier(n_estimators=100, random_state=42)
        if len(X_clf) > 0:
            clf_modelo.fit(X_clf, y_clf)
        
        st.markdown("Introduce las características de la interacción para predecir si el usuario comprará:")
        col_x, col_y = st.columns(2)
        with col_x:
            in_estres = st.slider("Estrés del Usuario (1-10)", 1, 10, 8)
            in_sentimiento = st.slider("Sentimiento NLP (-1.0 a 1.0)", -1.0, 1.0, -0.5)
            in_coincide = st.checkbox("¿El libro coincide con su tema de interés?")
        with col_y:
            in_interacciones = st.number_input("Mensajes enviados a Archie", 1, 50, 15)
            in_desc = st.selectbox("Descuento Ofrecido", [0.0, 0.10])
            in_premium = st.checkbox("🚨 Es un libro Premium (Chatbot)")
            
        if st.button("🔮 Predecir Probabilidad", type="primary"):
            if len(X_clf) == 0:
                st.error("No hay datos suficientes en este rango de fechas para predecir.")
            else:
                user_input = pd.DataFrame([[30, in_estres, in_interacciones, in_sentimiento, 8.5, in_desc, int(in_coincide), int(in_premium)]], columns=features_clf)
                prob = clf_modelo.predict_proba(user_input)[0][1]
                
                st.info(f"La probabilidad de venta es del **{prob * 100:.1f}%**")
                if in_premium:
                    st.caption("Nota: El modelo ha aprendido que las solicitudes Premium garantizan la conversión debido a la política de no retracto tras el pago de la pasarela.")

    # --- TAB 3: CLUSTERING (K-MEANS + PCA) ---
    with tab3:
        st.subheader("Descubrimiento de Buyer Personas y Estrategia de Pauta")
        st.markdown("La IA agrupa a los usuarios en tribus (Clusters) usando **K-Means**. Luego, cruza estos grupos con la demografía para sugerir la segmentación exacta de tus campañas publicitarias.")
        
        features_cluster = ['Nivel_Estres_Declarado', 'Interacciones_Chatbot', 'Sentimiento_NLP']
        df_cluster_data = df_u[features_cluster].dropna()
        
        if not df_cluster_data.empty and len(df_cluster_data) > 3:
            scaler = StandardScaler()
            data_scaled = scaler.fit_transform(df_cluster_data)
            
            pca = PCA(n_components=2)
            data_pca = pca.fit_transform(data_scaled)
            
            col_k, col_info = st.columns([1, 2])
            with col_k:
                n_clusters = st.slider("Cantidad de Segmentos (K):", 2, 5, 3)
                
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init='auto')
            clusters = kmeans.fit_predict(data_scaled)
            
            df_u['Cluster'] = clusters
            
            df_u['Grupo_Etario'] = pd.cut(df_u['Edad'], 
                                         bins=[0, 25, 35, 50, 100], 
                                         labels=['Gen Z (18-25)', 'Millennials (26-35)', 'Gen X (36-50)', 'Boomers (50+)'])
            
            df_plot = pd.DataFrame(data_pca, columns=['Componente 1 (Intensidad)', 'Componente 2 (Actividad)'])
            df_plot['Cluster'] = clusters
            
            fig_pca, ax_pca = plt.subplots(figsize=(10, 4))
            palette = sns.color_palette("husl", n_clusters)
            sns.scatterplot(data=df_plot, x='Componente 1 (Intensidad)', y='Componente 2 (Actividad)', 
                            hue='Cluster', palette=palette, s=100, ax=ax_pca)
            ax_pca.set_title(f"Mapa Bi-dimensional de Audiencias ({n_clusters} Segmentos)")
            st.pyplot(fig_pca)
            
            st.divider()
            
            st.subheader("🎯 Recomendaciones de Segmentación para Ads")
            st.markdown("Basado en las características predominantes de cada clúster, configura tus campañas así:")
            
            cols = st.columns(n_clusters)
            
            for i in range(n_clusters):
                cluster_data = df_u[df_u['Cluster'] == i]
                
                pais_top = cluster_data['Pais'].mode()[0] if not cluster_data.empty and 'Pais' in cluster_data.columns else "N/D"
                genero_top = cluster_data['Genero'].mode()[0] if not cluster_data.empty and 'Genero' in cluster_data.columns else "N/D"
                edad_top = cluster_data['Grupo_Etario'].mode()[0] if not cluster_data.empty else "N/D"
                tema_top = cluster_data['Tema_Frecuente'].mode()[0] if not cluster_data.empty else "N/D"
                
                estres_promedio = cluster_data['Nivel_Estres_Declarado'].mean()
                
                if estres_promedio >= 7.0:
                    tipo_campana = "🔥 Campaña de Venta Fuerte (Hard Sell)"
                    enfoque = "Sentido de urgencia, soluciones inmediatas. El usuario tiene un dolor activo."
                    color_alerta = "error"
                elif estres_promedio <= 4.0:
                    tipo_campana = "🌱 Campaña de Fidelización (Maintenance)"
                    enfoque = "Contenido de valor, prevención y hábitos. El usuario busca mejora continua."
                    color_alerta = "success"
                else:
                    tipo_campana = "🧲 Campaña de Adquisición (Lead Gen)"
                    enfoque = "Nutrición con muestras gratis. El usuario está explorando su situación."
                    color_alerta = "info"
                    
                with cols[i]:
                    st.markdown(f"### Segmento {i}")
                    if color_alerta == "error":
                        st.error(tipo_campana)
                    elif color_alerta == "success":
                        st.success(tipo_campana)
                    else:
                        st.info(tipo_campana)
                    
                    st.markdown(f"**Targeting Principal:**")
                    st.write(f"📍 **País:** {pais_top}")
                    st.write(f"👥 **Demografía:** {genero_top}, {edad_top}")
                    st.write(f"📚 **Gancho sugerido:** Libros de *{tema_top}*")
                    
                    st.markdown(f"**Perfil Psicológico:**")
                    st.write(f"Nivel de estrés prom: **{estres_promedio:.1f}/10**")
                    st.caption(enfoque)
        else:
            st.warning("No hay suficientes datos de usuarios para realizar la clusterización.")