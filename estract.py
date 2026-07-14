import os
from pypdf import PdfReader
from pydantic import BaseModel, Field
from typing import List, Optional
from langchain_community.llms import Ollama
from database import registrar_documento_completo # Importamos el guardado en BD

# 1. Definimos la estructura exacta que queremos extraer de la factura usando Pydantic
class ItemFactura(BaseModel):
    descripcion: str = Field(description="Nombre o descripción del producto")
    cantidad: float = Field(description="Cantidad adquirida")
    precio: Optional[float] = Field(None, description="Precio unitario")
    lote: Optional[str] = Field(None, description="Número de lote de fabricación")
    caducidad: Optional[str] = Field(None, description="Fecha de caducidad en formato AAAA-MM-DD")

class DocumentoEstructurado(BaseModel):
    tipo: str = Field(description="Tipo de documento, ej: Factura, Packing List, COA")
    numero: str = Field(description="Número de factura o documento")
    proveedor: str = Field(description="Nombre de la empresa proveedora")
    fecha: str = Field(description="Fecha de emisión del documento en formato AAAA-MM-DD")
    items: List[ItemFactura] = Field(description="Lista de productos/ítems detallados")

# 2. Función para leer texto de un PDF local
def extraer_texto_pdf(ruta_pdf):
    if not os.path.exists(ruta_pdf):
        raise FileNotFoundError(f"No se encontró el archivo: {ruta_pdf}")
    
    reader = PdfReader(ruta_pdf)
    texto = ""
    for pagina in reader.pages:
        texto += pagina.extract_text() or ""
    return texto

# 3. Función principal de evaluación con LangChain y Ollama
def evaluar_y_guardar_documento(ruta_pdf):
    print(f"[PROCESO] Leyendo PDF: {ruta_pdf}")
    texto_documento = extraer_texto_pdf(ruta_pdf)
    
    # Configuramos Ollama de forma local (usa 'llama3', 'mistral' o 'phi3')
    llm = Ollama(model="llama3", temperature=0)
    
    prompt = (
        "Analiza el siguiente texto extraído de un documento comercial y estructura la información. "
        "Debes responder ÚNICAMENTE con un objeto JSON válido que cumpla este esquema:\n"
        f"{DocumentoEstructurado.schema_json()}\n\n"
        f"Texto del documento:\n{texto_documento}"
    )
    
    print("[PROCESO] Enviando texto a Ollama local...")
    respuesta_raw = llm.invoke(prompt)
    
    # Parseamos la respuesta JSON del modelo
    import json
    try:
        datos = json.loads(respuesta_raw)
        
        # Estructuramos los datos para nuestra función de base de datos
        doc_info = {
            "tipo": datos.get("tipo", "Factura"),
            "numero": datos.get("numero"),
            "proveedor": datos.get("proveedor"),
            "fecha": datos.get("fecha")
        }
        
        lista_items = datos.get("items", [])
        
        # Guardamos en nuestra Base de Datos SQLite
        doc_id = registrar_documento_completo(doc_info, lista_items)
        return doc_id, doc_info
        
    except Exception as e:
        print(f"[ERROR] No se pudo estructurar el JSON de Ollama: {e}")
        return None, None