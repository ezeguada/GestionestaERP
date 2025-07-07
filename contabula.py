import pdfplumber
import pandas as pd
import re

pdf_path = r"C:\tabla_porhora.pdf"

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
df_final = procesar_pdf(pdf_path)

#print(df_final[0]["Datos"])

#for mostrable in df_final:
    
    #print(mostrable["ID"])
    #print(mostrable)