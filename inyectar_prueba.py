import sqlite3

DB_NAME = "control_documental.db"

def inyectar_lote_critico():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    try:
        # 1. Insertamos un documento de control de calidad (COA) de prueba
        cursor.execute("""
            INSERT INTO documentos (tipo_documento, numero_documento, proveedor, fecha_emision)
            VALUES ('COA', 'COA-2026-9912', 'Laboratorio Farmacéutico del Sur', '2026-07-10')
        """)
        doc_id = cursor.lastrowid
        
        # 2. Insertamos un ítem que vence en SEPTIEMBRE DE 2026 (Menos de 90 días desde hoy)
        cursor.execute("""
            INSERT INTO items_documento (documento_id, descripcion_producto, cantidad, precio_unitario, numero_lote, fecha_caducidad)
            VALUES (?, 'Principio Activo Crítico B', 150.0, 45.00, 'LOTE-CRIT-01', '2026-09-15')
        """, (doc_id,))
        
        conn.commit()
        print("✅ [SQL] Lote de prueba crítico inyectado con éxito en la base de datos local.")
    except sqlite3.Error as e:
        print(f"❌ Error al inyectar datos: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    inyectar_lote_critico()