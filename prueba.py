from cs50 import SQL
import pandas as pd

db = SQL("sqlite:///database.db")

caja = db.execute("SELECT * FROM formulario")
df = pd.DataFrame(caja).groupby("nombre_encargada")[["fecha", "sobranteposnet", "faltanteposnet", "sobranteefectivo", "faltanteefectivo"]]

print(df.head())