import sqlite3

conexion = sqlite3.connect(r'C:\Users\Ezequiel\Desktop\flask\flask\gestionesta\database.db')
cursor = conexion.cursor()

cursor.execute('''
        DELETE FROM productos
        WHERE id BETWEEN 30 AND 292
        ''')
        
# 5. Confirmar cambios
conexion.commit()