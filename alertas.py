import os
import sqlite3
import pandas as pd

DIRECTORIO_RAIZ = os.path.dirname(os.path.abspath(__file__))
RUTA_DB = os.path.join(DIRECTORIO_RAIZ, "agiliza_tech.db")
RUTA_EXCEL_SALIDA = os.path.join(DIRECTORIO_RAIZ, "alertas_caducidad.xlsx")

def generar_reporte_vencimientos():
    """
    Lee los registros de SQLite y actualiza el reporte Excel.
    Maneja excepciones en caso de que el archivo esté abierto.
    """
    try:
        conexion = sqlite3.connect(RUTA_DB)
        query = """
            SELECT proveedor, tipo_documento, numero_documento, 
                   descripcion_producto, numero_lote, fecha_caducidad, 
                   cantidad, estado 
            FROM documentos
        """
        df = pd.read_sql_query(query, conexion)
        conexion.close()
        
        if df.empty:
            df = pd.DataFrame(columns=[
                "proveedor", "tipo_documento", "numero_documento", 
                "descripcion_producto", "numero_lote", "fecha_caducidad", 
                "cantidad", "estado"
            ])

        df.to_excel(RUTA_EXCEL_SALIDA, index=False)
        return True, "¡Archivo 'alertas_caducidad.xlsx' actualizado!"

    except PermissionError:
        mensaje_error = (
            "El archivo 'alertas_caducidad.xlsx' está abierto en WPS Office o Excel.\n"
            "Por favor, ciérralo y vuelve a intentar."
        )
        return False, mensaje_error

    except Exception as e:
        return False, f"Error inesperado al generar reporte: {e}"