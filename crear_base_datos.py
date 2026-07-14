import sqlite3

# Nombre del archivo de base de datos que se creará localmente
DB_NAME = "control_documental.db"

# Tu diseño de base de datos en formato SQL
SQL_SCHEMA = """
-- Tabla principal para los Documentos Comerciales
CREATE TABLE IF NOT EXISTS documentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo_documento TEXT NOT NULL, -- 'Factura', 'Packing List', 'COA', etc.
    numero_documento TEXT NOT NULL UNIQUE,
    proveedor TEXT NOT NULL,
    fecha_emision TEXT,
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabla para el desglose de ítems/productos dentro del documento
CREATE TABLE IF NOT EXISTS items_documento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    documento_id INTEGER,
    descripcion_producto TEXT NOT NULL,
    cantidad REAL NOT NULL,
    precio_unitario REAL,
    numero_lote TEXT,         -- Vital para COA y trazabilidad
    fecha_caducidad TEXT,     -- Vital para control de calidad
    FOREIGN KEY (documento_id) REFERENCES documentos(id) ON DELETE CASCADE
);
"""

def inicializar_base_datos():
    try:
        # 1. Establecer conexión (Si el archivo no existe, SQLite lo crea automáticamente)
        conexion = sqlite3.connect(DB_NAME)
        cursor = conexion.cursor()
        
        # 2. Ejecutar las instrucciones SQL para crear las tablas
        cursor.executescript(SQL_SCHEMA)
        
        # 3. Guardar cambios y cerrar conexión
        conexion.commit()
        print(f"¡Éxito! Base de datos '{DB_NAME}' creada y configurada correctamente de forma local.")
        
    except sqlite3.Error as e:
        print(f"Error al inicializar la base de datos: {e}")
    finally:
        if conexion:
            conexion.close()

if __name__ == "__main__":
    inicializar_base_datos()