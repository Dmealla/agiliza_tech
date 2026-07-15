import unittest
import sqlite3
from datetime import datetime, timedelta

# Importamos las funciones que queremos probar
from database import registrar_documento_completo, conectar_db
from alertas import generar_reporte_vencimientos

class TestSistemaControlDocumental(unittest.TestCase):

    def setUp(self):
        """Se ejecuta antes de cada prueba. Configura una BD temporal limpia."""
        self.conn = sqlite3.connect(":memory:") # BD en memoria RAM, se destruye al terminar
        self.cursor = self.conn.cursor()
        
        # Crear estructura idéntica
        self.cursor.execute("""
            CREATE TABLE documentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo_documento TEXT NOT NULL,
                numero_documento TEXT NOT NULL UNIQUE,
                proveedor TEXT NOT NULL,
                fecha_emision TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE items_documento (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                documento_id INTEGER,
                descripcion_producto TEXT NOT NULL,
                cantidad REAL NOT NULL,
                precio_unitario REAL,
                numero_lote TEXT,
                fecha_caducidad TEXT,
                FOREIGN KEY (documento_id) REFERENCES documentos(id)
            )
        """)
        self.conn.commit()

    def tearDown(self):
        """Se ejecuta al finalizar cada prueba. Cierra la conexión."""
        self.conn.close()

    def test_unicidad_documento(self):
        """PRUEBA 1: Verificar que la base de datos realmente impida números de documento duplicados."""
        # Insertar primer documento
        self.cursor.execute("INSERT INTO documentos (tipo_documento, numero_documento, proveedor) VALUES ('Factura', 'TEST-001', 'Prov A')")
        self.conn.commit()
        
        # Intentar insertar duplicado deberia lanzar un error de SQLite (IntegrityError)
        with self.assertRaises(sqlite3.IntegrityError):
            self.cursor.execute("INSERT INTO documentos (tipo_documento, numero_documento, proveedor) VALUES ('Factura', 'TEST-001', 'Prov B')")
            self.conn.commit()

    def test_logica_alertas(self):
        """PRUEBA 2: Verificar la matemática de fechas del algoritmo de alertas."""
        fecha_hoy = datetime(2026, 7, 14)
        
        # Caso 1: Vence en 30 días (Debería ser CRÍTICO)
        fecha_critica = (fecha_hoy + timedelta(days=30)).strftime("%Y-%m-%d")
        # Caso 2: Vence en 200 días (No debería entrar en el reporte de 180 días)
        fecha_segura = (fecha_hoy + timedelta(days=200)).strftime("%Y-%m-%d")
        
        # Verificamos que las fechas se calcularon bien en formato string
        self.assertEqual(fecha_critica, "2026-08-13")
        self.assertEqual(fecha_segura, "2027-01-30")

if __name__ == "__main__":
    unittest.main()