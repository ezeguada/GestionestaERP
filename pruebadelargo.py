a = "Hora, NombreEcargada, Turno, VisaNombre1, VisaNombre2, VisaNombre3, VisaNombre4, VisaImporte1, VisaImporte2, \
        VisaImporte3, VisaImporte4, QrNombre, QrImporte, TotalPosnet, TransferenciasText, Transferencias, PedidosYaText, \
        PedidosYa, Cantidad20m, Cantidad10m, Cantidad2m, Cantidad1m, Cantidad500, Cantidad200, Cantidad100, Cantidad50, \
        Cantidad20, Cantidad10, Total20m, Total10m, Total2m, Total1m, Total500, Total200, Total100, Total50, Total20, Total10, \
        TotalEfectivo, Egresos, TotalEgresos, EntregaEfectivo, EntregaPosnet, TotalEfectivoSistema, TotalPosnetSistema, \
        SobrantEfectivo, SobrantePosnet, FaltanteEfectivo, FaltantePosnet, TotalCierre, TotalSistema, TotalDescuentosCierre, \
        TotalDescuentosSistema, Observaciones"
contador = 0
for letra in a:
    if letra == ",":
        contador+=1

print(contador)