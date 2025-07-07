import pandas as pd
import csv
import re
from datetime import datetime, timedelta


path = r'C:\Users\Ezequiel\Downloads\feliciaMarzo.csv'
#r"C:\esm.csv"

def redondear_hora(dt):
    if dt.minute >= 30:
        # Redondear hacia arriba: sumar una hora y reiniciar minutos
        return dt.replace(minute=0, second=0) + timedelta(hours=1)
    else:
        # Redondear hacia abajo: reiniciar minutos
        return dt.replace(minute=0, second=0)
    

def csv_to_dict(ruta):

    cadena_buscada = "ID"
    data = []

    # Leer el CSV y buscar la cadena
    with open(ruta, "r", encoding="latin-1") as file:
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
                    if (re.findall(r'\b\d{2}/\d{2}/\d{4}\b', cell) or re.findall(r'\b\d{2}\.\d{2}\.\d{4}\b', cell)) and not re.findall('Desde', cell):
                        #print('ok')
                        datalist = [elemento for elemento in row[0].split(';') if elemento != ""]
                        #print(datalist)
                        aux['datos'].append(datalist)  # Agregar la fila a 'datos'
                    continue

        # Agregar el último aux a data (si no está vacío)
        if aux:
            data.append(aux)

        #print(data)

        return data
    

def validar_formato_fecha(fecha_str):
    return (re.match(r'^\d{2}/\d{2}/\d{4} \d{1,2}:\d{2}$', fecha_str) or re.match(r'^\d{2}\.\d{2}\.\d{4} \d{1,2}:\d{2}$', fecha_str)) is not None


def procesar_registros(listas_registros):
    resultados = []
    
    for i, registros in enumerate([listas_registros['datos']], 1):
        #print(i, registros)
        total = timedelta()
        problemas = []
        registros_invalidos = []
        eventos = []
        
        try:
            # Validar y parsear registros
            for registro in registros:

                if len(registro) != 2:
                    registros_invalidos.append(str(registro))
                    continue
                    
                fecha_str, tipo = registro
                
                if tipo not in ['Entrada', 'Salida']:
                    registros_invalidos.append(str(registro))
                    continue
                    
                if not validar_formato_fecha(fecha_str):
                    registros_invalidos.append(str(registro))
                    continue
                
                try:
                    # Con formato de hora con puntos (Por lo genral en Bartolomé)
                    #fecha = datetime.strptime(fecha_str, '%d.%m.%Y %H:%M')
                    fecha = datetime.strptime(fecha_str, '%d/%m/%Y %H:%M')
                    if tipo == 'Entrada':
                        fecha = redondear_hora(fecha)
                    eventos.append((fecha, tipo))
                    print(fecha, tipo)
                except:
                    registros_invalidos.append(str(registro))
            
            # Ordenar eventos
            eventos.sort(key=lambda x: x[0])
            #print(eventos)
            
            # Eliminar duplicados (5 minutos de margen)
            limpios = []
            ultimo = None
            for evento in eventos:
                if ultimo:
                    if evento[1] == ultimo[1] and (evento[0] - ultimo[0]).total_seconds() < 3600:
                        # No se muestran las fichadas repetidas para evitar contaminación visual
                        #problemas.append(f"Registro duplicado: {evento[0].strftime('%d/%m %H:%M')} - {evento[1]}")
                        continue
                limpios.append(evento)
                ultimo = evento
            
            # Calcular jornadas
            entrada_actual = None
            for tiempo, tipo in limpios:
                if tipo == 'Entrada':
                    if entrada_actual:
                        problemas.append(f"Entrada solapada: {tiempo.strftime('%d/%m %H:%M')}")
                    entrada_actual = tiempo
                else:
                    if entrada_actual:
                        duracion = tiempo - entrada_actual
                        total += duracion
                        entrada_actual = None
                    else:
                        problemas.append(f"Salida sin entrada: {tiempo.strftime('%d/%m %H:%M')}")
            
            if entrada_actual:
                problemas.append(f"Entrada sin salida: {entrada_actual.strftime('%d/%m %H:%M')}")
            
            # Formatear resultado
            horas = total.total_seconds() / 3600
            resultados.append({
                'lista': i,
                'horas': f"{int(horas)}h {int((horas % 1) * 60):02d}m",
                'horasdec': round(horas, 2),
                'problemas': problemas,
                'registros_invalidos': registros_invalidos
            })
            
        except Exception as e:
            resultados.append({
                'lista': i,
                'error': str(e),
                'registros_invalidos': registros_invalidos
            })
    
    return resultados


def convertdata(datos):
    events = []
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
                #if tipo == 'Entrada':
                    #fecha_hora = redondear_hora(datetime.strptime(fecha_hora, '%d.%m.%Y %H:%M'))
                #print(fecha_hora,tipo)
                eventos.append((fecha_hora, tipo))
        aux = {
            'id':datos['id'],
            'nombre':datos['nombre'],
            'datos':eventos
        }
        events.append(aux)

    return events


def converttodf(listas_registros):
    futurodf = []
    for  lista in listas_registros:
        
        iterable = procesar_registros(lista)

        for res in iterable:
            data = {
                'ID': lista['id'],
                'Nombre': lista['nombre'],
                'Horas trabajadas': res['horas'],
                'Horas decimal': res['horasdec'],
                'Problemas': res['problemas']
            }

        futurodf.append(data)

    df = pd.DataFrame(futurodf)

    df.to_excel(r'C:\Users\Ezequiel\Downloads\feliciaoMarzoExcel.xlsx', index=False)

    return df


# Convierte el csv en una list of dicts con id, nombre y datos (contiene todo los records de fichadas)
resultado = csv_to_dict(path)

# Convierte "datos" en pares ordenados de "fecha" "hora" "(entrada o salida)"
listas_registros = convertdata(resultado)

df = converttodf(listas_registros)

# Ejecutar y mostrar resultados
for  lista in listas_registros:
    
    iterable = procesar_registros(lista)

    for res in iterable:
        print(f"\n- Nombre: {lista['nombre']}, ID: {lista['id']}")
        print(f"Horas totales: {res['horas']}")
        print(f"Registros inválidos: {len(res['registros_invalidos'])}")
        print(f'El registro invalido es {res['registros_invalidos']}')

        if res['problemas']:
            print("\nProblemas detectados:")
            for p in res['problemas']:
                print(f"- {p}")

