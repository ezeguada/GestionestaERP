from datetime import datetime, timedelta
from collections import defaultdict
import re

def validar_formato_fecha(fecha_str):
    return re.match(r'^\d{2}/\d{2}/\d{4} \d{1,2}:\d{2}$', fecha_str) is not None

def procesar_registros(listas_registros):
    resultados = []
    
    for i, registros in enumerate(listas_registros, 1):
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
                    fecha = datetime.strptime(fecha_str, '%d/%m/%Y %H:%M')
                    eventos.append((fecha, tipo))
                except:
                    registros_invalidos.append(str(registro))
            
            # Ordenar eventos
            eventos.sort(key=lambda x: x[0])
            
            # Eliminar duplicados (5 minutos de margen)
            limpios = []
            ultimo = None
            for evento in eventos:
                if ultimo:
                    if evento[1] == ultimo[1] and (evento[0] - ultimo[0]).total_seconds() < 300:
                        problemas.append(f"Registro duplicado: {evento[0].strftime('%d/%m %H:%M')} - {evento[1]}")
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

# Datos correctamente estructurados
listas_registros = [
    [  # Única lista con todos los registros
        ('01/02/2025 17:30', 'Entrada'),
        ('02/02/2025 2:02', 'Salida'),
        ('02/02/2025 21:04', 'Salida'),
        ('03/02/2025 16:16', 'Entrada'),
        ('04/02/2025 0:34', 'Salida'),
        ('06/02/2025 16:26', 'Entrada'),
        ('06/02/2025 23:08', 'Salida'),
        ('07/02/2025 18:20', 'Entrada'),
        ('08/02/2025 1:35', 'Salida'),
        ('08/02/2025 17:33', 'Entrada'),
        ('09/02/2025 1:37', 'Salida'),
        ('09/02/2025 17:31', 'Entrada')
    ]
]

# Ejecutar y mostrar resultados
resultados = procesar_registros(listas_registros)
print(resultados)

for res in resultados:
    print(f"\n● Lista {res['lista']} ●")
    print(f"Horas totales: {res['horas']}")
    print(f"Registros inválidos: {len(res['registros_invalidos'])}")
    
    if res['problemas']:
        print("\nProblemas detectados:")
        for p in res['problemas']:
            print(f"- {p}")