import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import os

DB_NAME = "control_documental.db"

def generar_reporte_vencimientos(dias_limite=180, archivo_salida="alertas_caducidad.xlsx"):
    """
    Analiza las fechas de caducidad guardadas en la base de datos local
    y genera un reporte en Excel con los lotes próximos a vencer.
    """
    # 1. Definir la fecha actual de referencia (Entorno de producción de 2026)
    fecha_hoy = datetime(2026, 7, 14)
    fecha_limite = fecha_hoy + timedelta(days=dias_limite)
    
    fecha_hoy_str = fecha_hoy.strftime("%Y-%m-%d")
    fecha_limite_str = fecha_limite.strftime("%Y-%m-%d")
    
    # 2. Conexión y consulta estructurada SQL
    conn = sqlite3.connect(DB_NAME)
    query = """
        SELECT d.proveedor, d.tipo_documento, d.numero_documento,
               i.descripcion_producto, i.numero_lote, i.fecha_caducidad, i.cantidad
        FROM documentos d
        JOIN items_documento i ON d.id = i.documento_id
        WHERE i.fecha_caducidad IS NOT NULL 
          AND i.fecha_caducidad != 'null'
          AND i.fecha_caducidad <= ?
    """
    
    try:
        # Convertir consulta en DataFrame
        df = pd.read_sql_query(query, conn, params=(fecha_limite_str,))
        conn.close()
        
        if df.empty:
            print("[INFO] No se encontraron lotes críticos próximos a vencer.")
            return False
            
        # 3. Clasificación de Criticidad (Lógica del script)
        # Convertimos la columna a objeto datetime para poder comparar
        df['fecha_caducidad_dt'] = pd.to_datetime(df['fecha_caducidad'], format='%Y-%m-%d')
        
        def asignar_estado(row):
            dias_restantes = (row['fecha_caducidad_dt'] - fecha_hoy).days
            if dias_restantes < 0:
                return "VENCIDO"
            elif dias_restantes <= 90:
                return "CRÍTICO (<90 días)"
            else:
                return "ADVERTENCIA"
                
        df['Estado'] = df.apply(asignar_estado, axis=1)
        
        # Eliminar columna auxiliar de fecha para la exportación limpia
        df = df.drop(columns=['fecha_caducidad_dt'])
        
        # 4. Escritura en Excel usando openpyxl
        with pd.ExcelWriter(archivo_salida, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name="Alertas_Vencimiento")
            
        print(f"✅ [ÉXITO] Reporte de alertas generado localmente en: {archivo_salida}")
        return True
        
    except Exception as e:
        print(f"❌ [ERROR] Falló la generación del reporte de alertas: {e}")
        return False

if __name__ == "__main__":
    generar_reporte_vencimientos()