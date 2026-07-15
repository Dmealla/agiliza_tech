import os
import sys

# --- SOLUCIÓN DE RUTAS LOCALES ---
# Obtiene la ruta de la carpeta donde está este script y la agrega al buscador de Python
ruta_script = os.path.dirname(os.path.abspath(__file__))
if ruta_script not in sys.path:
    sys.path.insert(0, ruta_script)
# ---------------------------------

import time
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Ahora Python encontrará perfectamente estos archivos en la misma carpeta
from extract import evaluar_y_guardar_documento
from alertas import generar_reporte_vencimientos

# Configuración de rutas locales
DIRECTORIO_RAIZ = r"F:\Documents\AGILIZATECH\AGILIZA_TECH\agiliza_tech"
CARPETA_ENTRADA = os.path.join(DIRECTORIO_RAIZ, "entrada_documentos")
CARPETA_PROCESADOS = os.path.join(DIRECTORIO_RAIZ, "procesados")
CARPETA_ERRORES = os.path.join(DIRECTORIO_RAIZ, "errores")

class VigilanteDocumentosHandler(FileSystemEventHandler):
    """Manejador de eventos que reacciona cuando se detecta un nuevo archivo."""
    
    def on_created(self, event):
        # Ignorar directorios
        if event.is_directory:
            return
            
        # Solo procesar archivos PDF
        if not event.src_path.lower().endswith('.pdf'):
            return
            
        ruta_archivo = os.path.abspath(event.src_path)
        nombre_archivo = os.path.basename(ruta_archivo)
        
        print(f"\n[DETECTADO] Nuevo archivo PDF encontrado: {nombre_archivo}")
        
        # Pequeña pausa para asegurar que el archivo se haya terminado de copiar por completo
        time.sleep(1.5)
        
        try:
            # 1. Ejecutar el motor de extracción (Ollama + LangChain + SQLite)
            doc_id, info = evaluar_y_guardar_documento(ruta_archivo)
            
            if doc_id:
                print(f"✅ [PROCESADO] Guardado con ID {doc_id} | {info['proveedor']} | {info['numero']}")
                
                # 2. Mover a la carpeta de procesados exitosos
                destino = os.path.join(CARPETA_PROCESADOS, nombre_archivo)
                shutil.move(ruta_archivo, destino)
                print(f"📁 [ARCHIVO MOVIDO] -> {CARPETA_PROCESADOS}")
                
                # 3. Actualizar automáticamente el Excel de alertas críticas de vencimiento
                print("[ANALIZANDO] Actualizando reporte de alertas en Excel...")
                generar_reporte_vencimientos()
                
            else:
                raise ValueError("El motor de IA no pudo estructurar correctamente los datos.")
                
        except Exception as e:
            print(f"❌ [ERROR PROCESAMIENTO] Falló el archivo {nombre_archivo}. Motivo: {e}")
            # Mover a la carpeta de errores para que el operador lo revise manualmente
            try:
                destino_error = os.path.join(CARPETA_ERRORES, nombre_archivo)
                shutil.move(ruta_archivo, destino_error)
                print(f"⚠️ [ARCHIVO MOVIDO A ERRORES] -> {CARPETA_ERRORES}")
            except Exception as ex:
                print(f"No se pudo mover el archivo a la carpeta de errores: {ex}")

def iniciar_vigilancia():
    # Asegurar que existan todas las carpetas necesarias
    for carpeta in [CARPETA_ENTRADA, CARPETA_PROCESADOS, CARPETA_ERRORES]:
        if not os.path.exists(carpeta):
            os.makedirs(carpeta)
            print(f"Creada carpeta del sistema: {carpeta}")
            
    # Configurar el observador de watchdog
    event_handler = VigilanteDocumentosHandler()
    observer = Observer()
    observer.schedule(event_handler, path=CARPETA_ENTRADA, recursive=False)
    
    print(f"\n=======================================================")
    print(f"👀 VIGILANTE ACTIVO - MONITOREANDO CARPETA LOCAL")
    print(f"Arrastra tus PDFs a: {CARPETA_ENTRADA}")
    print(f"Presiona Ctrl + C para detener el servicio.")
    print(f"=======================================================\n")
    
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n🛑 Servicio de vigilancia detenido por el usuario.")
    observer.join()

if __name__ == "__main__":
    iniciar_vigilancia()