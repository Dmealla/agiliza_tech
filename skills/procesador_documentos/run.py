#!/usr/bin/env python3
import sys
import os

# Agregamos la carpeta superior para que run.py pueda importar 'extract.py'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

try:
    from extract import evaluar_y_guardar_documento
except ImportError as e:
    print(f"Error: No se pudo importar el motor de extracción. Verifica que 'extract.py' esté en la carpeta raíz. Detalles: {e}")
    sys.exit(1)

def main():
    # Validamos que OpenClaw nos haya pasado la ruta del PDF como argumento
    if len(sys.argv) < 2:
        print("Error: No indicaste la ruta del PDF a procesar.")
        sys.exit(1)
        
    ruta_pdf = sys.argv[1]
    
    # Normalizamos la ruta del archivo para evitar problemas con diagonales inversas en Windows
    ruta_pdf = os.path.abspath(ruta_pdf)
    
    if not os.path.exists(ruta_pdf):
        print(f"Error: El archivo no existe en la ruta especificada: {ruta_pdf}")
        sys.exit(1)
        
    try:
        # Llamamos al motor principal de Python + LangChain + Ollama
        doc_id, info = evaluar_y_guardar_documento(ruta_pdf)
        
        if doc_id:
            # Esta respuesta formateada es la que OpenClaw leerá y enviará de vuelta al usuario
            print(f"✅ ¡Procesamiento Completo!\n"
                  f"• ID en Base de Datos: {doc_id}\n"
                  f"• Tipo de Documento: {info.get('tipo', 'Desconocido')}\n"
                  f"• Proveedor: {info.get('proveedor', 'Desconocido')}\n"
                  f"• Nro Documento: {info.get('numero', 'Sin número')}\n"
                  f"• Fecha Emisión: {info.get('fecha', 'Sin fecha')}\n"
                  f"Los datos de los productos y sus lotes correspondientes han sido guardados de manera estructurada.")
        else:
            print("❌ El documento pudo leerse pero ocurrió un error al estructurar la información con el modelo local.")
            
    except Exception as e:
        print(f"❌ Error crítico durante la ejecución de la herramienta: {str(e)}")

if __name__ == "__main__":
    main()