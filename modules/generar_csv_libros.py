import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os

# Fijamos una semilla para que los resultados sean reproducibles
np.random.seed(42)
random.seed(42)

# Definimos la cantidad de datos simulados
num_libros = 400

# Diccionario de temas y sus posibles tags asociados
temas_y_tags = {
    "Productividad": ["hábitos", "mañana", "enfoque", "tiempo", "metas", "disciplina"],
    "Ansiedad": ["estrés", "mindfulness", "paz mental", "respiración", "calma", "salud"],
    "Liderazgo": ["oficina", "equipos", "empatía", "management", "comunicación", "estrategia"],
    "Crecimiento Personal": ["autoestima", "motivación", "psicología", "cambio", "resiliencia"],
    "Finanzas Personales": ["ahorro", "inversión", "dinero", "presupuesto", "libertad financiera"]
}

# Listas para almacenar los datos
ids = []
titulos = []
paginas_list = []
temas_list = []
tags_list = []
tendencias = []
afaps = []
precios = []
fechas_creacion = []

# Fecha base para las creaciones (ej. último año)
fecha_base = datetime.now() - timedelta(days=365)

for i in range(1, num_libros + 1):
    # 1. ID del Libro
    es_premium = random.random() < 0.25 # 25% de los libros serán Premium CB
    if es_premium:
        id_libro = f"CB-{i:03d}"
    else:
        id_libro = f"AF-{i:03d}"
    ids.append(id_libro)
    
    # 2. Tema Principal y Título básico
    tema = random.choice(list(temas_y_tags.keys()))
    temas_list.append(tema)
    titulos.append(f"Guía de {tema} Vol. {random.randint(1, 100)}")
    
    # 3. Páginas (Según la estrategia de Asset Foundry: 50 a 65 páginas)
    paginas = random.randint(50, 65)
    paginas_list.append(paginas)
    
    # 4. Tags (Seleccionamos 3 a 5 tags al azar del tema correspondiente)
    tags_seleccionados = random.sample(temas_y_tags[tema], random.randint(3, 5))
    tags_list.append(", ".join(tags_seleccionados))
    
    # 5. Nivel de Tendencia del Mercado (7.0 a 10.0)
    tendencia = round(random.uniform(7.0, 10.0), 1)
    tendencias.append(tendencia)
    
    # 6. Cantidad de Herramientas AFAP (3 a 5)
    cantidad_afap = random.randint(3, 5)
    afaps.append(cantidad_afap)
    
    # 7. Precio de Venta (LÓGICA PARA LA REGRESIÓN LINEAL)
    # Creamos una fórmula base para que el modelo ML tenga algo que predecir
    precio_base = 8.0 if es_premium else 5.0
    impacto_paginas = (paginas - 50) * 0.20  # $0.20 extra por cada página adicional a 50
    impacto_tendencia = tendencia * 0.5      # $0.50 extra por cada punto de tendencia
    impacto_afap = cantidad_afap * 0.50         # $0.50 extra por cada herramienta AFAP
    ruido_aleatorio = random.uniform(-1.0, 1.0) # Un poco de ruido para que no sea una fórmula perfecta
    
    precio_final = round(precio_base + impacto_paginas + impacto_tendencia + impacto_afap + ruido_aleatorio, 2)
    precios.append(precio_final)
    
    # 8. Fecha de Creación
    fecha_random = fecha_base + timedelta(days=random.randint(0, 335), hours=random.randint(0, 23))
    fechas_creacion.append(fecha_random.strftime("%Y-%m-%d %H:%M:%S"))

# Crear el DataFrame de Pandas
df_libros = pd.DataFrame({
    "ID_Libro": ids,
    "Fecha_Creacion": fechas_creacion,
    "Titulo": titulos,
    "Paginas": paginas_list,
    "Tema_Principal": temas_list,
    "Tags": tags_list,
    "Nivel_Tendencia_Mercado": tendencias,
    "Herramientas_AFAP": afaps,
    "Precio_Venta": precios
})

# Mostrar las primeras 5 filas para verificar
print(df_libros.head())

# Exportar a CSV
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_dir = os.path.join(base_dir, "databases_asset_foundry")
os.makedirs(db_dir, exist_ok=True)

nombre_archivo = os.path.join(db_dir, "dataset_libros_asset_foundry.csv")
df_libros.to_csv(nombre_archivo, index=False, encoding='utf-8')

print(f"\n¡Éxito! Se ha generado el archivo en '{nombre_archivo}' con {num_libros} registros.")