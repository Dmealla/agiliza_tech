import sqlite3

DB_NAME = "control_documental.db"

def mostrar_registros_locales():
    """Consulta y muestra en consola todos los documentos e ítems guardados."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # 1. Consultar Documentos
        print("\n=== TABLA: DOCUMENTOS ===")
        cursor.execute("SELECT id, tipo_documento, numero_documento, proveedor, fecha_emision FROM documentos")
        documentos = cursor.fetchall()
        
        if not documentos:
            print("No hay documentos registrados aún.")
        for doc in documentos:
            print(f"ID: {doc[0]} | Tipo: {doc[1]} | Nro: {doc[2]} | Proveedor: {doc[3]} | Fecha: {doc[4]}")
            
        # 2. Consultar Ítems
        print("\n=== TABLA: ITEMS_DOCUMENTO ===")
        cursor.execute("SELECT id, documento_id, descripcion_producto, cantidad, numero_lote, fecha_caducidad FROM items_documento")
        items = cursor.fetchall()
        
        if not items:
            print("No hay ítems registrados aún.")
        for item in items:
            print(f"ID: {item[0]} | Doc ID: {item[1]} | Producto: {item[2]} | Cant: {item[3]} | Lote: {item[4]} | Caducidad: {item[5]}")
            
        conn.close()
    except sqlite3.Error as e:
        print(f"Error al leer la base de datos: {e}")

if __name__ == "__main__":
    mostrar_registros_locales()