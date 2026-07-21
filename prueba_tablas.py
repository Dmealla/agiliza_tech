import pdfplumber
import pandas as pd

def extraer_tablas_pdf(ruta_pdf):
    """
    Abre un PDF y extrae las tablas de forma exacta utilizando pdfplumber.
    """
    print(f"Procesando el documento: {ruta_pdf}...\n")
    
    todas_las_filas = []

    # Abrimos el PDF de forma estructurada
    with pdfplumber.open(ruta_pdf) as pdf:
        for pagina in pdf.pages:
            # Buscamos todas las tablas en la página actual
            tablas = pagina.extract_tables()
            
            for tabla in tablas:
                for fila in tabla:
                    # Limpiamos los saltos de línea o celdas nulas
                    fila_limpia = [str(celda).replace('\n', ' ').strip() if celda else "" for celda in fila]
                    
                    # Guardamos la fila solo si no está completamente vacía
                    if any(fila_limpia):
                        todas_las_filas.append(fila_limpia)

    if not todas_las_filas:
        print("No se encontraron tablas estructuradas en este PDF.")
        return

    # Convertimos los datos a un DataFrame (Tabla virtual de Pandas) para verlos alineados
    df = pd.DataFrame(todas_las_filas)
    
    print("--- DATOS EXTRAÍDOS CON EXACTITUD ---")
    # Imprimimos la tabla en la consola
    print(df.to_string(index=False, header=False))

if __name__ == "__main__":
    # IMPORTANTE: Asegúrate de tener este archivo PDF en la misma carpeta de tu proyecto
    ruta_archivo = "1. CARTA DE SOLICITUD.pdf" 
    extraer_tablas_pdf(ruta_archivo)