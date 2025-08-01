import pdfplumber
import pandas as pd
import re
from datetime import datetime

pdf_path = r"C:\tabla_porhora.pdf"

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

def procesar_pdf(ruta_pdf):
    # Regex para extraer múltiples bloques "ID X Nombre Y" por página
    id_nombre_pattern = re.compile(r"ID (\d+) Nombre (.+?)(?=\s{2,}|Departamento)", re.DOTALL)

    #DictRes = {}
    ListRes = []
    
    datos = []
    
    with pdfplumber.open(ruta_pdf) as pdf:
        for page in pdf.pages:
            texto = page.extract_text()
            tablas = page.extract_tables()
            
            # Encontrar TODOS los ID y Nombres en la página
            matches = list(id_nombre_pattern.finditer(texto))
            
            if not matches:
                continue  # Si no hay IDs, saltar la página
            
            # Asignar tablas a cada ID/Nombre (asumiendo mismo orden)
            for i, match in enumerate(matches):
                nuevo_id = match.group(1)
                nuevo_nombre = match.group(2).strip()
                #print(nuevo_id)
                
                # Buscar si ya existe una entrada para este ID/Nombre
                clave = f"{nuevo_id}|{nuevo_nombre}"
                tabla_existente = next((item for item in datos if item['Clave'] == clave), None)
                
                if not tabla_existente:
                    tabla_existente = {
                        'Clave': clave,
                        'ID': nuevo_id,
                        'Nombre': nuevo_nombre,
                        'Datos': []
                    }
                    datos.append(tabla_existente)
                    #print(tabla_existente)
                
                # Asignar tablas correspondientes (si hay suficientes)
                if i < len(tablas):
                    tabla = tablas[i]
                    filas_limpias = [fila for fila in tabla if any(celda.strip() for celda in fila)]
                    
                    # Filtrar encabezados duplicados
                    if tabla_existente['Datos'] and filas_limpias:
                        if filas_limpias[0] == tabla_existente['Datos'][-1]:
                            filas_limpias = filas_limpias[1:]
                    
                    tabla_existente['Datos'].extend(filas_limpias)

                    # Agregar cada diccionario a la lista
                    ListRes.append(tabla_existente)

    return ListRes

# Ejecutar y mostrar resultados
listadiccionario = procesar_pdf(pdf_path)
#print(listadiccionario[0]["Datos"])

for datos in listadiccionario:
    # Extraer tablas de cada página

    eventos = []
    for sublista in datos["Datos"]:
        #print(sublista)
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
    df.insert(0,"id",datos["ID"])

    df[["Horas trabajadas", "Horas numérico"]] = df.apply(lambda row: calcular_horas(row["Entrada"], row["Salida"]), 
                                                            axis=1, result_type="expand")
    
    print(df)