---
name: procesador
description: Procesa, extrae y guarda en la base de datos local los datos de facturas, COAs o Packing Lists en PDF.
user-invocable: true
tools:
  - name: procesar_pdf
    script: python run.py
---

# Habilidad de Procesamiento Documental

Esta habilidad permite procesar y guardar documentos comerciales (como Facturas, Certificados de Análisis o Packing Lists) en formato PDF directamente en la base de datos local utilizando Python y Ollama.

## Cómo usarla:
Pasa la ruta del archivo PDF que se desea procesar como argumento a la herramienta.

Ejemplo:
`procesar_pdf "F:\Documents\AGILIZATECH\11 CONTROL DE CALIDAD DEL PRODUCTO TERMINADO.pdf"`