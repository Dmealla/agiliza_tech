import sqlite3
from datetime import datetime

DB_NAME = "control_documental.db"

def conectar_db():
    return sqlite3.connect(DB_NAME)

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
            cursor.execute("""
                INSERT INTO items_documento (documento_id, descripcion_producto, cantidad, precio_unitario, numero_lote, fecha_caducidad)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (doc_id, item['descripcion'], item['cantidad'], item.get('precio'), item.get('lote'), item.get('caducidad')))
            
        conn.commit()
        return doc_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()