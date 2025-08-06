import sqlite3

conexion = sqlite3.connect(r'C:\Users\Ezequiel\Desktop\flask\flask\gestionesta\database.db')
cursor = conexion.cursor()


cursor.execute("ALTER TABLE stock DROP COLUMN cantidadbase")

cursor.execute("ALTER TABLE stock ADD COLUMN \"1\" INTEGER")

cursor.execute("SELECT * FROM stock")