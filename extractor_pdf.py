import pdfplumber
import pandas as pd

def procesar_documento_senasag(ruta_pdf):
    """
    Recibe la ruta de un PDF, extrae las tablas de forma exacta con pdfplumber 
    y devuelve un DataFrame de Pandas limpio.
    """
    todas_las_filas = []

    try:
        with pdfplumber.open(ruta_pdf) as pdf:
            for pagina in pdf.pages:
                tablas = pagina.extract_tables()
                
                for tabla in tablas:
                    for fila in tabla:
                        # Limpiamos los saltos de línea y guardamos la fila
                        fila_limpia = [str(celda).replace('\n', ' ').strip() if celda else "" for celda in fila]
                        if any(fila_limpia):
                            todas_las_filas.append(fila_limpia)

        if not todas_las_filas:
            return pd.DataFrame() # Devuelve una tabla vacía si no hay datos

        # Convertimos los datos extraídos a un DataFrame de Pandas
        df = pd.DataFrame(todas_las_filas)
        return df

    except Exception as e:
        raise Exception(f"Error procesando el PDF: {e}")