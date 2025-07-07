import pdfplumber
import pandas as pd

pdf_path = r"C:\tabla_porhora.pdf"
tables = []

with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        # Extraer tablas de cada página
        page_tables = page.extract_tables()
        #print(page_tables)
        for table in page_tables:
            print(table)
            # Convertir cada tabla a DataFrame y agregarla a la lista
            df_temp = pd.DataFrame(table[1:], columns=table[0])
            #print(df_temp.head())
            tables.append(df_temp)
            #print(tables)

# Combinar todas las tablas en un único DataFrame
#final_df = pd.concat(tables, ignore_index=True)

#print(final_df.head())