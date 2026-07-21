import os
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Importamos tus propios módulos llamándolos directamente por su nombre
from extractor_pdf import procesar_documento_senasag
from extract import evaluar_y_guardar_documento
from alertas import generar_reporte_vencimientos
from ia_ollama import extraer_texto_pdf, consultar_llama3
from extract import guardar_validacion_checklist

# ==========================================
# 1. FUNCIONES DE ACCIÓN (LÓGICA)
# ==========================================

def iniciar_extraccion_en_hilo(ruta_archivo):
    """Ejecuta la lectura en segundo plano para no congelar la ventana."""
    try:
        datos_extraidos = procesar_documento_senasag(ruta_archivo)
        
        if datos_extraidos.empty:
            messagebox.showwarning("Aviso", "El documento no contenía tablas legibles.")
        else:
            print("--- DATOS RECIBIDOS EN LA APP PRINCIPAL ---")
            print(datos_extraidos)
            messagebox.showinfo("¡Éxito!", "Documento procesado correctamente.\nRevisa la consola.")
            
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un problema al leer el PDF:\n{e}")

def cargar_pdf():
    """Abre el explorador de Windows y lanza el hilo de procesamiento."""
    ruta_archivo = filedialog.askopenfilename(
        title="Seleccionar documento SENASAG",
        filetypes=[("Archivos PDF", "*.pdf")]
    )
    
    if ruta_archivo:
        messagebox.showinfo("Procesando", "Iniciando lectura del documento...")
        hilo_proceso = threading.Thread(target=iniciar_extraccion_en_hilo, args=(ruta_archivo,))
        hilo_proceso.start()

def mostrar_alertas():
    """Función puente para conectar tu módulo de alertas."""
    try:
        generar_reporte_vencimientos()
        messagebox.showinfo("Reporte", "Reporte de vencimientos generado.")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo generar el reporte:\n{e}")

def abrir_guia_tramite():
    """Abre una ventana emergente con el paso a paso detallado para trámites."""
    ventana_guia = tk.Toplevel()
    ventana_guia.title("Guía de Trámites de Importación")
    ventana_guia.geometry("650x650")
    ventana_guia.configure(padx=15, pady=15)

    canvas = tk.Canvas(ventana_guia)
    scrollbar = ttk.Scrollbar(ventana_guia, orient="vertical", command=canvas.yview)
    frame_scroll = ttk.Frame(canvas)

    frame_scroll.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=frame_scroll, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    marco_paso1 = tk.LabelFrame(frame_scroll, text="PASO 1: Verificación de Documentos", font=("Arial", 12, "bold"), fg="#2E7D32", padx=10, pady=10)
    marco_paso1.pack(fill="x", pady=5)
    texto_paso1 = (
        "Documentos a cargar y verificar:\n"
        "• Factura.\n"
        "• Lista de empaque.\n"
        "• COA o Certificado de análisis.\n\n"
        "Importante: Verifica la vigencia del registro/padrón (el producto debe estar vigente) y asegúrate de que la presentación coincida exactamente entre el sistema y los documentos.\n"
        "NOTA: Si todo es correcto, iniciar el trámite. No alterar ningún documento sin notificar al proveedor."
    )
    tk.Label(marco_paso1, text=texto_paso1, justify="left", wraplength=550).pack(anchor="w")

    marco_paso2 = tk.LabelFrame(frame_scroll, text="PASO 2: Carta y Formulario", font=("Arial", 12, "bold"), fg="#1565C0", padx=10, pady=10)
    marco_paso2.pack(fill="x", pady=5)
    texto_paso2 = (
        "Información clave para la Carta:\n"
        "• Fecha: El día que se cargará al sistema.\n"
        "• Conversiones: Si la presentación es en ML, convertir a LITROS (Ej: 20 ml x 300 = 6000 ml / 1000 = 6 Lt.). Aplicar misma fórmula de Gr. a Kg.\n"
        "• Dosis (Biológico/Vacunas): Multiplicar cantidad x cantidad de DOSIS.\n"
        "• Vigencia: NO importar productos con menos de 3 meses de vigencia.\n"
        "• Valor: El valor total debe estar en $U$. Si es otra moneda, convertir y explicar el tipo de cambio.\n"
        "• Peso Neto: Colocar el que indica la LISTA DE EMPAQUE (no la sumatoria de ítems)."
    )
    tk.Label(marco_paso2, text=texto_paso2, justify="left", wraplength=550).pack(anchor="w")

    marco_paso3 = tk.LabelFrame(frame_scroll, text="PASO 3: Llenado en el Sistema", font=("Arial", 12, "bold"), fg="#E65100", padx=10, pady=10)
    marco_paso3.pack(fill="x", pady=5)
    texto_paso3 = (
        "Campos del sistema:\n"
        "• Destino del Producto: Seleccionar SIEMPRE 'COMERCIAL', 'MATERIA PRIMA' o 'MUESTRA COMERCIAL'.\n"
        "• Certificados Sanitarios que Acompañan: Llenar este campo cuando se realice REPOSICIÓN, AMPLIACIÓN o REEMPLAZO DE PERMISO."
    )
    tk.Label(marco_paso3, text=texto_paso3, justify="left", wraplength=550).pack(anchor="w")

# ==========================================
# SECCIÓN: CHECKLIST CON INTELIGENCIA ARTIFICIAL
# ==========================================

def analizar_documento_real(tipo_documento, etiqueta_estado, ruta_archivo):
    """Lee el PDF y le pide a Ollama 3 que verifique si es válido."""
    etiqueta_estado.config(text="⏳ Leyendo PDF...", fg="#FF9800")
    ventana_checklist.update()
    
    # 1. Extraemos el texto
    texto_pdf = extraer_texto_pdf(ruta_archivo)
    
    if "Error" in texto_pdf:
        etiqueta_estado.config(text="❌ Error de lectura", fg="red")
        return

    etiqueta_estado.config(text="🤖 Llama 3 pensando...", fg="#FF9800")
    ventana_checklist.update()

    # 2. Le damos instrucciones a Llama 3 según el documento
    if tipo_documento == "Factura":
        instrucciones = "Eres un asistente del SENASAG. Responde SOLO con la palabra 'APROBADO' si el texto parece ser una factura comercial válida, o 'RECHAZADO' si no lo es."
    elif tipo_documento == "Lista de Empaque":
        instrucciones = "Eres un asistente del SENASAG. Responde SOLO con 'APROBADO' si encuentras el peso neto en este documento, o 'RECHAZADO' si no está."
    else:
        instrucciones = "Eres un asistente del SENASAG. Responde SOLO 'APROBADO' si el documento es válido, o 'RECHAZADO' si no lo es."

    # 3. Consultamos a la IA local
    respuesta_ia = consultar_llama3(instrucciones, texto_pdf)
    
    # 4. Actualizamos la interfaz según la respuesta
    if "APROBADO" in respuesta_ia.upper():
        etiqueta_estado.config(text="✔️ Aprobado", fg="#4CAF50")
    else:
        etiqueta_estado.config(text="❌ Revisar", fg="red")
        print(f"Nota de la IA para {tipo_documento}: {respuesta_ia}")

def procesar_documento_checklist(tipo_documento, etiqueta_estado):
    """Permite al usuario elegir un archivo y lanza el análisis con IA."""
    ruta_archivo = filedialog.askopenfilename(
        title=f"Cargar {tipo_documento}",
        filetypes=[("Archivos PDF", "*.pdf")]
    )
    if ruta_archivo:
        # Ejecutamos el análisis en un hilo para no congelar la ventana del checklist
        hilo_ia = threading.Thread(target=analizar_documento_real, args=(tipo_documento, etiqueta_estado, ruta_archivo))
        hilo_ia.start()

def mostrar_resumen_y_guardar(lbl_fac, lbl_emp, lbl_coa):
    """Muestra un resumen final leyendo las etiquetas y guarda en SQLite."""
    estado_factura = lbl_fac.cget("text")
    estado_empaque = lbl_emp.cget("text")
    estado_coa = lbl_coa.cget("text")
    
    resumen = (
        "--- RESUMEN DE VALIDACIÓN ---\n"
        f"Factura: {estado_factura}\n"
        f"Lista de Empaque: {estado_empaque}\n"
        f"COA: {estado_coa}\n\n"
        "¿Deseas guardar estos datos en la Base de Datos?"
    )
    
    respuesta = messagebox.askyesno("Resumen de Validación", resumen)
    
    if respuesta:
        try:
            guardar_validacion_checklist(estado_factura, estado_empaque, estado_coa)
            messagebox.showinfo("Guardado", "¡Datos guardados exitosamente en agiliza_tech.db!")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar: {e}")

def abrir_checklist_ia():
    """Construye la ventana visual para el escaneo inteligente de documentos."""
    global ventana_checklist 
    
    ventana_checklist = tk.Toplevel()
    ventana_checklist.title("Checklist Inteligente - IA Local")
    ventana_checklist.geometry("550x400")
    ventana_checklist.configure(padx=20, pady=20)

    tk.Label(ventana_checklist, text="Asistente de Validación Documental", font=("Arial", 14, "bold")).pack(pady=(0, 20))

    # --- Fila 1: Factura ---
    frame_factura = tk.Frame(ventana_checklist)
    frame_factura.pack(fill="x", pady=10)
    tk.Label(frame_factura, text="1. Factura Comercial:", width=20, anchor="w", font=("Arial", 10, "bold")).pack(side="left")
    lbl_estado_fac = tk.Label(frame_factura, text="Pendiente", width=15, fg="gray")
    lbl_estado_fac.pack(side="left", padx=10)
    tk.Button(frame_factura, text="Cargar y Leer", command=lambda: procesar_documento_checklist("Factura", lbl_estado_fac)).pack(side="left")

    # --- Fila 2: Lista de Empaque ---
    frame_empaque = tk.Frame(ventana_checklist)
    frame_empaque.pack(fill="x", pady=10)
    tk.Label(frame_empaque, text="2. Lista de Empaque:", width=20, anchor="w", font=("Arial", 10, "bold")).pack(side="left")
    lbl_estado_emp = tk.Label(frame_empaque, text="Pendiente", width=15, fg="gray")
    lbl_estado_emp.pack(side="left", padx=10)
    tk.Button(frame_empaque, text="Cargar y Leer", command=lambda: procesar_documento_checklist("Lista de Empaque", lbl_estado_emp)).pack(side="left")

    # --- Fila 3: COA ---
    frame_coa = tk.Frame(ventana_checklist)
    frame_coa.pack(fill="x", pady=10)
    tk.Label(frame_coa, text="3. Certificado de Análisis:", width=20, anchor="w", font=("Arial", 10, "bold")).pack(side="left")
    lbl_estado_coa = tk.Label(frame_coa, text="Pendiente", width=15, fg="gray")
    lbl_estado_coa.pack(side="left", padx=10)
    tk.Button(frame_coa, text="Cargar y Leer", command=lambda: procesar_documento_checklist("COA", lbl_estado_coa)).pack(side="left")

    ttk.Separator(ventana_checklist, orient='horizontal').pack(fill='x', pady=20)

    # Botón Final
    tk.Button(
        ventana_checklist, 
        text="Verificar Resumen y Guardar", 
        command=lambda: mostrar_resumen_y_guardar(lbl_estado_fac, lbl_estado_emp, lbl_estado_coa), 
        bg="#1565C0", 
        fg="white", 
        font=("Arial", 12, "bold")
    ).pack(pady=10)


# ==========================================
# 2. INTERFAZ GRÁFICA (VISTA)
# ==========================================

def construir_interfaz():
    """Construye la ventana visual de la aplicación."""
    ventana = tk.Tk()
    ventana.title("AGILIZA TECH - Panel Principal")
    # Ampliamos un poco la ventana para que quepan los 4 botones cómodamente
    ventana.geometry("500x400")
    ventana.configure(padx=20, pady=20)

    # Título principal
    lbl_titulo = tk.Label(ventana, text="Gestión de Documentos SENASAG", font=("Arial", 16, "bold"))
    lbl_titulo.pack(pady=(0, 20))

    # Botón 1
    btn_cargar = tk.Button(ventana, text="1. Cargar y Leer PDF", command=cargar_pdf, bg="#2196F3", fg="white", font=("Arial", 12), width=25)
    btn_cargar.pack(pady=10)

    # Botón 2
    btn_alertas = tk.Button(ventana, text="2. Ver Alertas de Vencimiento", command=mostrar_alertas, bg="#FF9800", fg="white", font=("Arial", 12), width=25)
    btn_alertas.pack(pady=10)

    # Botón 3
    btn_guia = tk.Button(ventana, text="3. Ver Guía de Trámite", command=abrir_guia_tramite, bg="#4CAF50", fg="white", font=("Arial", 12), width=25)
    btn_guia.pack(pady=10)

    # Botón 4 (¡NUEVO!)
    btn_checklist = tk.Button(ventana, text="4. Iniciar Checklist Inteligente", command=abrir_checklist_ia, bg="#9C27B0", fg="white", font=("Arial", 12), width=25)
    btn_checklist.pack(pady=10)

    # Encender la ventana (UNA SOLA VEZ AL FINAL)
    ventana.mainloop()

# Punto de entrada
if __name__ == "__main__":
    construir_interfaz()