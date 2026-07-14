import sqlite3
import pandas as pd
from datetime import datetime

DB_NAME = "control_documental.db"

def conectar_db():
    return sqlite3.connect(DB_NAME)

# --- 1. FUNCIONES DE VALIDACIÓN ---
def validar_fecha(fecha_str):
    try:
        datetime.strptime(fecha_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def validar_lote(lote_str):
    if not lote_str or len(lote_str.strip()) < 3:
        return False
    return True

# --- 2. REGISTRO EN LA BASE DE DATOS ---
def registrar_documento_completo(doc_info, lista_items):
    conn = conectar_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO documentos (tipo_documento, numero_documento, proveedor, fecha_emision)
            VALUES (?, ?, ?, ?)
        """, (doc_info['tipo'], doc_info['numero'], doc_info['proveedor'], doc_info['fecha']))
        
        doc_id = cursor.lastrowid
        
        for item in lista_items:
            if not validar_fecha(item['caducidad']):
                raise ValueError(f"Fecha de caducidad inválida para el lote {item['lote']}")
            if not validar_lote(item['lote']):
                raise ValueError(f"Número de lote inválido para el ítem {item['descripcion']}")
                
            cursor.execute("""
                INSERT INTO items_documento (documento_id, descripcion_producto, cantidad, precio_unitario, numero_lote, fecha_caducidad)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (doc_id, item['descripcion'], item['cantidad'], item['precio'], item['lote'], item['caducidad']))
            
        conn.commit()
        print(f"¡Documento e ítems registrados localmente con ID: {doc_id}!")
        return doc_id  # Devolvemos el ID para poder usarlo en la exportación
    except Exception as e:
        conn.rollback()
        print(f"Error en el registro: {e}")
        return None
    finally:
        conn.close()

# --- 3. TU FUNCIÓN DE EXPORTACIÓN (OPELCLAW) ---
def exportar_para_opelclaw(documento_id, ruta_salida_excel="salida_opelclaw.xlsx"):
    conn = conectar_db()
    query = """
        SELECT d.tipo_documento, d.numero_documento, d.proveedor, d.fecha_emision,
               i.descripcion_producto, i.cantidad, i.precio_unitario, i.numero_lote, i.fecha_caducidad
        FROM documentos d
        JOIN items_documento i ON d.id = i.documento_id
        WHERE d.id = ?
    """
    df = pd.read_sql_query(query, conn, params=(documento_id,))
    conn.close()
    
    if df.empty:
        print("No se encontraron datos para exportar.")
        return
    
    df.to_excel(ruta_salida_excel, index=False, sheet_name="Datos_Capturados")
    print(f"Archivo exportado para Opelclaw en: {ruta_salida_excel}")


# --- 4. PRUEBA DE FUNCIONAMIENTO (FLUJO COMPLETO) ---
if __name__ == "__main__":
    # Simulamos los datos que un operador ingresaría desde un formulario
    datos_factura = {
        "tipo": "Factura",
        "numero": "FAC-2026-0001",
        "proveedor": "Proveedor Químico S.A.",
        "fecha": "2026-07-14"
    }
    
    items_factura = [
        {
            "descripcion": "Materia Prima Tipo A",
            "cantidad": 500.0,
            "precio": 12.50,
            "lote": "LOTE-9988X",
            "caducidad": "2028-12-31"
        }
    ]
    
    # Ejecutamos el flujo: Registrar -> Obtener ID -> Exportar a Opelclaw
    nuevo_id = registrar_documento_completo(datos_factura, items_factura)
    
    if nuevo_id:
        exportar_para_opelclaw(nuevo_id, "salida_opelclaw_FAC0001.xlsx")