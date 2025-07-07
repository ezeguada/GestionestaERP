import pandas as pd
import csv
import re
from datetime import datetime, timedelta
from collections import defaultdict

path = r"C:\esm.csv"


def csv_to_dict(ruta):

    cadena_buscada = "ID"
    data = []

    # Leer el CSV y buscar la cadena
    with open(ruta, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        aux = {}  # Inicializar aux como un diccionario vacío

        for row in reader:
            if any(cadena_buscada in cell for cell in row):
                idlist = [elemento for elemento in row[0].split(';') if elemento != ""]
                #print(lista_sin_vacios[1], lista_sin_vacios[3])
                # Si se encuentra la cadena, guardar el diccionario actual en data
                if aux:  # Solo si aux no está vacío
                    data.append(aux)
                # Reiniciar aux con la nueva estructura
                aux = {
                    'id': idlist[1],  # Guardar la fila actual como 'id'
                    'nombre': idlist[3],
                    'datos': []  # Inicializar 'datos' como una lista vacía
                }
            else:
                # Si no se encuentra la cadena, agregar la fila a 'datos'
                if 'datos' not in aux and data:
                    aux['datos'] = []  # Asegurarse de que 'datos' exista

                for cell in row:
                    if re.findall(r'\b\d{2}/\d{2}/\d{4}\b', cell) and not re.findall('Desde', cell):
                        datalist = [elemento for elemento in row[0].split(';') if elemento != ""]
                        aux['datos'].append(datalist)  # Agregar la fila a 'datos'
                    continue

        # Agregar el último aux a data (si no está vacío)
        if aux:
            data.append(aux)

        return data


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


def procesar_registros(listas_registros):
    # Umbral para considerar registros duplicados (en minutos)
    UMBRAL_DUPLICADOS = 5
    resultados = []

    for i, registros in enumerate(listas_registros, 1):
        try:
            # Parsear fechas y ordenar registros
            registros_parsed = [(datetime.strptime(r[0], '%d/%m/%Y %H:%M'), r[1]) 
                               for r in registros]
            registros_ordenados = sorted(registros_parsed, key=lambda x: x[0])
            
            # Eliminar registros duplicados
            registros_limpios = []
            ultimo_tipo = None
            ultimo_tiempo = None
            
            for tiempo, tipo in registros_ordenados:
                if ultimo_tipo == tipo:
                    diferencia = tiempo - ultimo_tiempo
                    if diferencia < timedelta(minutes=UMBRAL_DUPLICADOS):
                        continue  # Saltar registro duplicado
                registros_limpios.append((tiempo, tipo))
                ultimo_tipo = tipo
                ultimo_tiempo = tiempo

            # Agrupar por días
            dias = defaultdict(list)
            for tiempo, tipo in registros_limpios:
                dia = tiempo.date()
                dias[dia].append((tiempo, tipo))

            # Procesar cada día
            total_horas = timedelta()
            problemas = []
            registro_activo = None
            entrada_pendiente = None

            for dia, eventos in sorted(dias.items()):
                for tiempo, tipo in eventos:
                    if tipo == 'Entrada':
                        if registro_activo is None:
                            registro_activo = tiempo
                        else:
                            problemas.append(f"Día {dia}: Entrada múltiple a las {tiempo.time()}")
                    elif tipo == 'Salida':
                        if registro_activo:
                            jornada = tiempo - registro_activo
                            total_horas += jornada
                            registro_activo = None
                        else:
                            problemas.append(f"Día {dia}: Salida sin entrada previa a las {tiempo.time()}")
                
                if registro_activo:
                    problemas.append(f"Día {dia}: Entrada sin salida a las {registro_activo.time()}")
                    registro_activo = None

            # Formatear resultados
            horas_totales = total_horas.total_seconds() / 3600
            resultados.append({
                'lista': i,
                'horas_totales': f"{int(horas_totales)}h {int((horas_totales % 1) * 60)}m",
                'problemas': problemas,
                'dias_problematicos': len(problemas)
            })
            
        except Exception as e:
            resultados.append({
                'lista': i,
                'error': f"Error procesando lista: {str(e)}"
            })

    return resultados


# Mostrar los resultados
resultado = csv_to_dict(path)
print(resultado[1]['datos'])

for datos in resultado:
    # Extraer tablas de cada página
    eventos = []
    for sublista in datos["datos"]:
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
    #print(datos)
    df.insert(0, "id", datos["nombre"])

    #df[["Horas trabajadas", "Horas numérico"]] = df.apply(lambda row: calcular_horas(row["Entrada"], row["Salida"]), 
    #                                                        axis=1, result_type="expand")

print(df.tail())
