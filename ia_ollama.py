# Archivo: ia_ollama.py
import requests
import pdfplumber

def extraer_texto_pdf(ruta_archivo):
    """Extrae el texto de un PDF para que la IA pueda leerlo."""
    texto_completo = ""
    try:
        with pdfplumber.open(ruta_archivo) as pdf:
            for pagina in pdf.pages:
                texto = pagina.extract_text()
                if texto:
                    texto_completo += texto + "\n"
        return texto_completo
    except Exception as e:
        return f"Error: {e}"

def consultar_llama3(prompt, texto_documento):
    """Envía el texto y las instrucciones a Ollama de forma local."""
    url = "http://localhost:11434/api/generate"
    
    prompt_completo = f"{prompt}\n\nTexto del documento:\n{texto_documento}"
    
    datos = {
        "model": "llama3",
        "prompt": prompt_completo,
        "stream": False
    }
    
    try:
        respuesta = requests.post(url, json=datos)
        if respuesta.status_code == 200:
            return respuesta.json()['response'].strip()
        else:
            return "Error en el servidor de IA."
    except Exception:
        return "Error: Asegúrate de que Ollama esté abierto en tu PC."

def extraer_dato_especifico(tipo_dato, texto_documento):
    """Pide a Llama 3 que extraiga un dato muy puntual de un texto, sin dar explicaciones."""
    url = "http://localhost:11434/api/generate"
    
    # Instrucción estricta para que la IA no hable de más
    prompt = (
        f"Eres un experto en extracción de datos aduaneros. "
        f"Tu única tarea es encontrar el '{tipo_dato}' en el siguiente documento. "
        f"Responde SOLO con el valor exacto encontrado (número y unidad de medida). "
        f"NO escribas oraciones completas, NO des explicaciones. Si no lo encuentras, responde 'No encontrado'."
    )
    
    prompt_completo = f"{prompt}\n\nTexto del documento:\n{texto_documento}"
    
    datos = {
        "model": "llama3",
        "prompt": prompt_completo,
        "stream": False
    }
    
    try:
        respuesta = requests.post(url, json=datos)
        if respuesta.status_code == 200:
            return respuesta.json()['response'].strip()
        else:
            return "Error en servidor IA"
    except Exception:
        return "Error de conexión local"