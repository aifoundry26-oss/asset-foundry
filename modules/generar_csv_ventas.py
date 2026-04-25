import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os
import zipfile

# Fijamos la semilla para reproducibilidad
np.random.seed(42)
random.seed(42)

# 1. Cargar los datasets previos
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_dir = os.path.join(base_dir, "databases_asset_foundry")

try:
    df_usuarios = pd.read_csv(os.path.join(db_dir, 'dataset_usuarios_asset_foundry.csv'))
    df_libros = pd.read_csv(os.path.join(db_dir, 'dataset_libros_asset_foundry.csv'))
except FileNotFoundError:
    print(f"⚠️ Error: No se encontraron los archivos previos en {db_dir}")
    exit()

# 2. Configuración de la simulación
num_interacciones = 1000
ids_interaccion = []
fechas = []
usuarios_list = []
libros_list = []
descuentos = []
compras = []

# Copia de los libros disponibles para consumir los CB
df_libros_disponibles = df_libros.copy()

# Fecha base para simular el último mes de operación
fecha_inicio = datetime.now() - timedelta(days=30)

for i in range(1, num_interacciones + 1):
    # Generar ID y Fecha aleatoria en los últimos 30 días
    ids_interaccion.append(f"INT-{i:04d}")
    fecha_random = fecha_inicio + timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))
    fechas.append(fecha_random.strftime("%Y-%m-%d %H:%M:%S"))
    
    # Seleccionar un usuario y un libro al azar
    usuario = df_usuarios.sample(1).iloc[0]
    libro = df_libros_disponibles.sample(1).iloc[0]
    
    # Si el libro es premium (CB), solo puede interactuar una sola vez con un único usuario
    es_cb = str(libro['ID_Libro']).startswith('CB')
    if es_cb:
        df_libros_disponibles = df_libros_disponibles.drop(libro.name)
    
    usuarios_list.append(usuario['ID_Usuario'])
    libros_list.append(libro['ID_Libro'])
    
    # Simular si Archie le ofreció un descuento para motivarlo (10% o 0%)
    descuento_ofrecido = random.choice([0.0, 0.10])
    descuentos.append(descuento_ofrecido)
    
    # --- LÓGICA MATEMÁTICA PARA EL MODELO DE CLASIFICACIÓN ---
    # Calculamos la probabilidad real de que este usuario compre este libro
    probabilidad_compra = 0.05 # Probabilidad base muy baja (5%)
    
    # Regla 1: Si el libro trata sobre el tema que le interesa al usuario, la probabilidad se dispara
    if usuario['Tema_Frecuente'] == libro['Tema_Principal']:
        probabilidad_compra += 0.45
        
    # Regla 2: Usuarios con alto estrés son más propensos a buscar soluciones urgentes (comprar)
    if usuario['Nivel_Estres_Declarado'] >= 7:
        probabilidad_compra += 0.20
        
    # Regla 3: Si el libro es tendencia en el mercado, es más atractivo
    if libro['Nivel_Tendencia_Mercado'] >= 8.0:
        probabilidad_compra += 0.15
        
    # Regla 4: Si se le ofreció un descuento, sube la probabilidad un poco
    if descuento_ofrecido > 0:
        probabilidad_compra += 0.10
        
    # Los libros premium (generados a demanda) asumen una venta exitosa garantizada
    if es_cb:
        probabilidad_compra = 1.0
    else:
        # Limitamos la probabilidad máxima al 95% para que siempre haya margen de error humano
        probabilidad_compra = min(0.95, probabilidad_compra)
    
    # Determinar si compró (1) o no compró (0) usando la probabilidad calculada
    compro = np.random.choice([1, 0], p=[probabilidad_compra, 1 - probabilidad_compra])
    compras.append(compro)

# 3. Crear el DataFrame final
df_ventas = pd.DataFrame({
    "ID_Interaccion": ids_interaccion,
    "Fecha": fechas,
    "ID_Usuario": usuarios_list,
    "ID_Libro": libros_list,
    "Descuento_Ofrecido": descuentos,
    "Compro": compras
})

# Ordenar por fecha para mayor realismo
df_ventas = df_ventas.sort_values(by="Fecha").reset_index(drop=True)

# Exportar a CSV
os.makedirs(db_dir, exist_ok=True)
nombre_archivo = os.path.join(db_dir, "dataset_ventas_asset_foundry.csv")
df_ventas.to_csv(nombre_archivo, index=False, encoding='utf-8')

# Mostrar resumen
compras_totales = df_ventas['Compro'].sum()
tasa_conversion = (compras_totales / num_interacciones) * 100

print(df_ventas.head())
print(f"\n¡Éxito! Archivo '{nombre_archivo}' generado.")
print(f"Total de Interacciones: {num_interacciones}")
print(f"Ventas Exitosas: {compras_totales} (Tasa de conversión: {tasa_conversion:.1f}%)")

# 4. Crear el archivo ZIP con los 3 datasets
nombre_zip = os.path.join(base_dir, "dataset_asset_foundry.zip")
archivos_a_comprimir = [
    os.path.join(db_dir, "dataset_libros_asset_foundry.csv"),
    os.path.join(db_dir, "dataset_usuarios_asset_foundry.csv"),
    os.path.join(db_dir, "dataset_ventas_asset_foundry.csv")
]

print(f"\nComprimiendo archivos en {os.path.basename(nombre_zip)}...")
with zipfile.ZipFile(nombre_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
    for arch in archivos_a_comprimir:
        if os.path.exists(arch):
            # Guardamos en el ZIP solo con el nombre del archivo, no toda la ruta de Windows
            zf.write(arch, os.path.basename(arch))

print(f"📦 ¡Todos los datasets fueron empaquetados exitosamente y listos para subir al Dashboard!")