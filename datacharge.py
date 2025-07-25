import sqlite3
import pandas as pd
import re
import sqlite3

conexion = sqlite3.connect("database.db")
cursor = conexion.cursor()

path = r'C:\Users\Ezequiel\Downloads\productos.csv'

data = pd.read_csv(path).fillna(0).to_dict('list')

filas = []
for i in range(len(data['ITEM'])):
    filas.append((
        int(data['id_empresa'][i]),
        data['ITEM'][i],
        float(data['COSTO'][i]),
        float(data['PORCENTAJE'][i]),
        float(data['IVA'][i]),
        float(data['EFECTIVO'][i])
    ))

#print(filas)

cursor.executemany('''
        INSERT OR REPLACE INTO productos (id_empresa, nombre, costo, ganancia, iva, efectivo)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', filas)
        
# 5. Confirmar cambios
conexion.commit()
print(f"Se insertaron {len(filas)} registros exitosamente!")

# 6. Cerrar conexión
if conexion:
    conexion.close()