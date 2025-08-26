import sqlite3
import pandas as pd
import re
import sqlite3

conexion = sqlite3.connect(r'C:\Users\Ezequiel\Desktop\flask\flask\gestionesta\database.db')
cursor = conexion.cursor()

path = r'C:\Users\Ezequiel\Downloads\stock.csv'

data = pd.read_csv(path).fillna(0).to_dict('list')
#print(data["producto"])
listaproductos = []
#productos = cursor.execute("SELECT id, nombre FROM productos")
#print(cursor.execute("SELECT * FROM productos WHERE id = 426").fetchone())
for producto in data["producto"]:
    algo = cursor.execute("SELECT id FROM productos WHERE nombre = ?", (producto,))
    #print(algo.fetchone()[0])
    try:
        id = algo.fetchone()[0]
        listaproductos.append(id)
    except:
        continue

data["producto"] = listaproductos

filas = []
for i in range(len(data['producto'])):
    filas.append((
        int(data['id_empresa'][i]),
        data['producto'][i],
        int(data['1'][i]),
        int(data['2'][i]),
    ))
print(filas)

#cursor.executemany("INSERT OR REPLACE INTO stock (id_empresa, id_producto, 1, 2) VALUES (?, ?, ?, ?)", filas)
        
cursor.executemany("INSERT OR REPLACE INTO stock (id_empresa, id_producto, local_1, local_2) VALUES (?, ?, ?, ?)", filas)

# 5. Confirmar cambios
conexion.commit()
print(f"Se insertaron {len(filas)} registros exitosamente!")

# 6. Cerrar conexión
if conexion:
    conexion.close()