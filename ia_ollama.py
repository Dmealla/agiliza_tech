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