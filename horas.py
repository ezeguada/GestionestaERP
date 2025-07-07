import pdfplumber
import pandas as pd
from datetime import datetime


pdf_path = r"C:\tabla_porhora.pdf"
tables = []

# Paso 3: Calcular diferencia en horas y minutos
# Función para calcular ambas columnas
def calcular_horas(entrada, salida):
    formato = "%d/%m/%Y %H:%M"
    entrada_dt = datetime.strptime(entrada, formato)
    salida_dt = datetime.strptime(salida, formato)
    delta = salida_dt - entrada_dt
    total_segundos = delta.total_seconds()
    
    # Calcular formato HH:MM
    horas = int(total_segundos // 3600)
    minutos = int((total_segundos % 3600) // 60)
    formato_hhmm = f"{horas}:{minutos:02d}"
    
    # Calcular formato numérico (ej: 6.53 para 6h32m)
    horas_numerico = round(total_segundos / 3600, 2)  # Redondeado a 2 decimales
    
    return formato_hhmm, horas_numerico

with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        # Extraer tablas de cada página
        page_tables = page.extract_tables()
        # Paso 1: Extraer eventos y limpiar valores None
        eventos = []
        for sublista in page_tables[0]:
            for i in range(0, len(sublista), 2):
                if i+1 >= len(sublista):
                    break
                fecha_hora = sublista[i]
                tipo = sublista[i+1]
                if fecha_hora is None or tipo is None:
                    continue
                eventos.append((fecha_hora, tipo))

        # Paso 2: Emparejar Entradas con Salidas
        entradas_salidas = []
        entrada_actual = None

        for fecha_hora, tipo in eventos:
            if tipo == "Entrada":
                entrada_actual = fecha_hora
            elif tipo == "Salida" and entrada_actual is not None:
                entradas_salidas.append({"Entrada": entrada_actual, "Salida": fecha_hora})
                entrada_actual = None  # Resetear para el próximo par

        # Paso 3: Crear el DataFrame
        df = pd.DataFrame(entradas_salidas)

        df[["Horas trabajadas", "Horas numérico"]] = df.apply(lambda row: calcular_horas(row["Entrada"], row["Salida"]), 
                                                              axis=1, result_type="expand")
        
        print(df)