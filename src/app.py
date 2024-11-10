import os
from bs4 import BeautifulSoup
import requests
import time
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

url = "https://ycharts.com/companies/TSLA/revenues"

# Crea una sesión para mantener las cookies y configuraciones
session = requests.Session()

# Actualiza el encabezado de la sesión con un User-Agent válido para simular que la solicitud viene de un navegador real. Esto ayuda a evitar bloqueos
session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"})

# Realiza una solicitud GET a la URL
response = session.get(url)

time.sleep(2)

if response.status_code == 403:
    print("Acceso denegado, verifique las cabeceras o espere.")
else:
    html_data = response.text


# Transformamos el HTML plano en un HTML real (estructurado y anidado, con forma de árbol)
soup = BeautifulSoup(response.text, 'html.parser') #

tables = soup.find_all("table")


for index, table in enumerate(tables):
    print(f"Tabla {index}:")
    print(table.prettify())  # Esto imprimirá la tabla en un formato más legible


# Cogemos las tablas 0 y 1 para concatenarlas y graficar los datos

table_indices = [0, 1]  # Índices de las tablas a concatenar

# Crear una lista para almacenar los DataFrames
dfs = []

# Iterar sobre los índices de las tablas seleccionadas
for table_index in table_indices:
    # Extraer las filas de la tabla
    rows = tables[table_index].find_all('tr')
    
    # Crear una lista para almacenar los datos de cada tabla
    data = []
    
    # Extraer los encabezados de las columnas
    headers = [header.text.strip() for header in rows[0].find_all('th')]
    
    # Si no hay encabezados en la tabla, puedes asumir nombres genéricos
    if not headers:
        headers = ["Column " + str(i) for i in range(len(rows[0].find_all('td')))]
    
    # Extraer los datos de las filas
    for row in rows[1:]:
        cols = row.find_all('td')
        if len(cols) > 0:  # Si la fila tiene datos
            data.append([col.text.strip() for col in cols])
    
    # Convertir los datos a un DataFrame
    df = pd.DataFrame(data, columns=headers)
    dfs.append(df)

# Concatenar los DataFrames en una sola tabla
tesla_revenue = pd.concat(dfs, ignore_index=True)

# Mostrar el DataFrame concatenado
print(tesla_revenue)

# Con la siguiente función convertimos a números la columna 'Value'
def convert_value(value):
    # Si el valor es un string
    if isinstance(value, str):
        if 'B' in value:
            # Eliminar 'B' y convertir a float, multiplicar por 1,000,000,000
            return float(value.replace('B', '').strip()) * 1e9
        elif 'M' in value:
            # Eliminar 'M' y convertir a float, multiplicar por 1,000,000
            return float(value.replace('M', '').strip()) * 1e6
    # Si el valor ya es un número (float), devolverlo tal cual
    return value


# Ordenamos la tabla según la fecha para que aparezca bien en el gráfico
tesla_revenue = tesla_revenue.sort_values(by='Date', ascending = True)

# Convertir la columna "Date" a formato datetime
tesla_revenue['Date'] = pd.to_datetime(tesla_revenue['Date'])
tesla_revenue['Value'] = tesla_revenue['Value'].apply(convert_value)

# Verificar si hay valores NaN en la columna 'Date'
print(tesla_revenue[tesla_revenue['Date'].isna()])

# Verificar si hay valores NaN en la columna 'Value'
print(tesla_revenue[tesla_revenue['Value'].isna()])


plt.figure(figsize=(20, 10))
sns.lineplot(data=tesla_revenue, x='Date', y='Value')

plt.title('Evolución de los ingresos de Tesla')
plt.xlabel('Fecha')
plt.ylabel('Ingresos (en miles de millones)')

plt.xticks(rotation=45)
plt.tight_layout()

plt.show()