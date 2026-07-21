# Archivo: extract.py
import sqlite3

# ==========================================
# FUNCIONES PARA EL BOTÓN 1 (TABLAS)
# ==========================================

def evaluar_y_guardar_documento(datos):
    """
    Función puente. Más adelante aquí escribiremos la lógica para 
    guardar las tablas extraídas en la base de datos o en Excel.
    """
    print("Módulo de tablas conectado. Datos listos para ser evaluados y guardados.")
    pass

# ==========================================
# FUNCIONES PARA EL BOTÓN 4 (IA OLLAMA)
# ==========================================

def crear_tabla_si_no_existe():
    """Crea la tabla en SQLite si es la primera vez que se ejecuta."""
    conexion = sqlite3.connect("agiliza_tech.db")
    cursor = conexion.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registro_documentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            estado_factura TEXT,
            estado_empaque TEXT,
            estado_coa TEXT
        )
    ''')
    conexion.commit()
    conexion.close()

def guardar_validacion_checklist(factura, empaque, coa):
    """Guarda el resultado de la IA en la base de datos SQLite."""
    crear_tabla_si_no_existe()
    
    conexion = sqlite3.connect("agiliza_tech.db")
    cursor = conexion.cursor()
    
    cursor.execute('''
        INSERT INTO registro_documentos (estado_factura, estado_empaque, estado_coa)
        VALUES (?, ?, ?)
    ''', (factura, empaque, coa))
    
    conexion.commit()
    conexion.close()
    print("Datos de IA guardados en la base de datos con éxito.")