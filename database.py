import sqlite3
import os

# Determinamos la ruta de la base de datos en el directorio del proyecto
DIRECTORIO_RAIZ = os.path.dirname(os.path.abspath(__file__))
RUTA_DB = os.path.join(DIRECTORIO_RAIZ, "agiliza_tech.db")

def inicializar_base_datos():
    """Crea la base de datos y la tabla de documentos si no existen."""
    conexion = sqlite3.connect(RUTA_DB)
    cursor = conexion.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            proveedor TEXT NOT NULL,
            tipo_documento TEXT DEFAULT 'Importacion/SENASAG',
            numero_documento TEXT,
            descripcion_producto TEXT DEFAULT 'N/A',
            numero_lote TEXT DEFAULT 'N/A',
            fecha_caducidad TEXT,
            cantidad INTEGER DEFAULT 0,
            estado TEXT DEFAULT 'Procesado'
        )
    """)
    conexion.commit()
    conexion.close()

def insertar_documento(proveedor, numero_documento, lista_productos):
    """
    Inserta múltiples registros en la base de datos a partir de la lista de productos 
    extraída por la IA de un solo documento.
    """
    inicializar_base_datos()
    conexion = sqlite3.connect(RUTA_DB)
    cursor = conexion.cursor()
    
    ids_generados = []
    
    # Recorremos la lista de productos para guardar cada lote como una fila
    for producto in lista_productos:
        descripcion = producto.get("descripcion", "Sin descripcion")
        lote = producto.get("lote", "S/N")
        fecha_vencimiento = producto.get("fecha_vencimiento", None)
        # Extraer cantidad (puede venir como texto o numero, intentamos convertirla)
        try:
            cantidad = int(producto.get("cantidad", 0))
        except ValueError:
            cantidad = 0

        cursor.execute("""
            INSERT INTO documentos 
            (proveedor, numero_documento, descripcion_producto, numero_lote, fecha_caducidad, cantidad, tipo_documento)
            VALUES (?, ?, ?, ?, ?, ?, 'Importacion/SENASAG')
        """, (proveedor, numero_documento, descripcion, lote, fecha_vencimiento, cantidad))
        
        ids_generados.append(cursor.lastrowid)
        
    conexion.commit()
    conexion.close()
    
    return ids_generados # Retorna todos los IDs guardados