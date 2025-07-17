import sqlite3
import pandas as pd
import re
import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

path = r'C:\Users\Ezequiel\Downloads\precios.csv'

data = pd.read_csv(path).fillna(0) #.to_dict('list')

print(data)


def convert_value(x):
    if isinstance(x, str):
        # Reemplazar comas por puntos
        x = x.replace(',', '.')
        # Extraer número y convertir si hay "%"
        if '%' in x:
            try:
                return float(re.sub(r'[^\d.]', '', x)) / 100  # Elimina todo excepto números y "."
            except:
                return x  # Si falla, devolver el original (ej: "N/A%")
        # Si no tiene "%", intentar convertir a float (ej: "25,75" → 25.75)
        try:
            return float(x)
        except:
            return x  # Mantener strings no numéricas (ej: "A")
    return x  # Devolver números o otros tipos sin cambios

def determinar_tipos_sql(lista):
    tipos_sql = []
    for elemento in lista:
        tipo_python = type(elemento)
        
        if tipo_python == int:
            tipo_sql = "INTEGER"
        elif tipo_python == float:
            tipo_sql = "REAL"
        elif tipo_python == str:
            tipo_sql = "TEXT"
        elif tipo_python == bool:
            tipo_sql = "INTEGER"  # SQLite no tiene BOOLEAN, usa 0/1
        elif elemento is None:
            tipo_sql = "NULL"    # No es un tipo, pero indica nulabilidad
        else:
            tipo_sql = "BLOB"     # Para bytes o tipos no estándar
        
        tipos_sql.append(tipo_sql)
    
    return tipos_sql

def tipo_sql_definitivo(lista):
    tipos = determinar_tipos_sql(lista)
    
    if "BLOB" in tipos:
        return "BLOB"
    elif "TEXT" in tipos:
        return "TEXT"
    elif "REAL" in tipos:
        return "REAL"
    elif "INTEGER" in tipos:
        return "INTEGER"
    else:
        return "NULL"  # Caso extremo (todos son None)

def crear_tabla(datos, nombre):
    # Generar la sentencia CREATE TABLE dinámicamente
    columnas_sql = []
    for columna, valores in datos.items():
        tipo = tipo_sql_definitivo(valores)
        columnas_sql.append(f"{columna} {tipo}")

    create_table_sql = f"CREATE TABLE IF NOT EXISTS {nombre} ({', '.join(columnas_sql)})"
    cursor.execute(create_table_sql)

    conn.commit()
    conn.close()

def cargar_datos(data, nombre):
    data.index = data.index.rename('id')  # Renombrar el índice como 'id'
    data.reset_index(inplace=True)      # Mover el índice a una columna regular
    # Conexión a SQLite y carga del DataFrame
    with sqlite3.connect('database.db') as conn:
        data.to_sql(name=nombre, con=conn, if_exists='append', index=False,  dtype={'id': 'INTEGER PRIMARY KEY'})

#data = data.applymap(convert_value) ##.to_dict('list')

#print(data)

#cargar_datos(data,'productos')

'''
cursor.execute('SELECT * FROM metodo_cobro')
rows = cursor.fetchall()
print(rows)
'''