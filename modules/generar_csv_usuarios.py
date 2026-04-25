import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os

# Fijamos la semilla para reproducibilidad
np.random.seed(42)
random.seed(42)

# Definimos la cantidad de usuarios
num_usuarios = 100

# Temas disponibles en Asset Foundry
temas = ["Productividad", "Ansiedad", "Liderazgo", "Crecimiento Personal", "Finanzas Personales"]
lista_paises = ['Argentina', 'Bolivia', 'Chile', 'Colombia', 'Costa Rica', 'Cuba', 'Ecuador', 'El Salvador', 'España', 'Estados Unidos', 'Guatemala', 'Honduras', 'México', 'Nicaragua', 'Panamá', 'Paraguay', 'Perú', 'Puerto Rico', 'República Dominicana', 'Uruguay', 'Venezuela']

# Listas para almacenar los datos
ids_usuario = []
edades = []
temas_frecuentes = []
niveles_estres = []
interacciones = []
sentimientos = []
fechas_registro = []
generos = []
paises = []

# Fecha base para los registros (ej. último año)
fecha_base = datetime.now() - timedelta(days=365)

for i in range(1, num_usuarios + 1):
    # 1. ID del Usuario
    ids_usuario.append(f"USR-{i:03d}")
    
    # 2. Edad (Distribución realista entre 18 y 65 años, con pico en los 30s)
    edad = int(np.random.normal(loc=32, scale=10))
    edad = max(18, min(65, edad)) # Limitamos para no tener edades fuera de rango
    edades.append(edad)
    
    # 3. Tema Frecuente
    tema = random.choice(temas)
    temas_frecuentes.append(tema)
    
    # 4. Nivel de Estrés Declarado (1 al 10)
    estres = random.randint(1, 10)
    niveles_estres.append(estres)
    
    # 5. Interacciones con el Chatbot (Correlacionado con el estrés)
    # Lógica: Si está más estresado, tiende a chatear más con Archie
    interacciones_base = random.randint(5, 20)
    interacciones_extra = int(estres * 2.5) 
    interacciones.append(interacciones_base + interacciones_extra)
    
    # 6. Sentimiento NLP (-1.0 a 1.0)
    # Lógica: A mayor estrés, el texto suele ser más negativo (se acerca a -1.0)
    # Estrés 10 -> Sentimiento tiende a -0.8 // Estrés 1 -> Sentimiento tiende a 0.8
    sentimiento_base = 1.0 - (estres * 0.2)
    # Añadimos un poco de ruido aleatorio
    ruido = random.uniform(-0.3, 0.3)
    sentimiento_final = round(max(-1.0, min(1.0, sentimiento_base + ruido)), 2)
    sentimientos.append(sentimiento_final)
    
    # 7. Fecha de Registro
    fecha_random = fecha_base + timedelta(days=random.randint(0, 335), hours=random.randint(0, 23))
    fechas_registro.append(fecha_random.strftime("%Y-%m-%d %H:%M:%S"))
    
    # 8. Género y País
    generos.append(random.choice(['Masculino', 'Femenino']))
    paises.append(random.choice(lista_paises))

# Crear el DataFrame
df_usuarios = pd.DataFrame({
    "ID_Usuario": ids_usuario,
    "Fecha_Registro": fechas_registro,
    "Genero": generos,
    "Pais": paises,
    "Edad": edades,
    "Tema_Frecuente": temas_frecuentes,
    "Nivel_Estres_Declarado": niveles_estres,
    "Interacciones_Chatbot": interacciones,
    "Sentimiento_NLP": sentimientos
})

# Mostrar las primeras filas
print(df_usuarios.head())

# Exportar a CSV
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_dir = os.path.join(base_dir, "databases_asset_foundry")
os.makedirs(db_dir, exist_ok=True)

nombre_archivo = os.path.join(db_dir, "dataset_usuarios_asset_foundry.csv")
df_usuarios.to_csv(nombre_archivo, index=False, encoding='utf-8')

print(f"\n¡Éxito! Se ha generado el archivo en '{nombre_archivo}' con {num_usuarios} registros.")