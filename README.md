# 🤖 Agente IA de Soporte Operativo e Informativo

Un asistente virtual inteligente basado en **Arquitectura RAG (Retrieval-Augmented Generation)** desarrollado para responder consultas operativas y comerciales con base en la documentación oficial de la empresa, garantizando respuestas precisas y control de alucinaciones.

🔗 **Demo en Producción:** [https://alura-agente-ia-techmarket.streamlit.app](https://alura-agente-ia-techmarket.streamlit.app)

---

## 💡 Ejemplos de Preguntas y Respuestas del Agente

### ❓ Pregunta 1 (Envíos y Fechas Especiales)
> **Usuario:** *"¿Cuáles son los tiempos de entrega para compras en CyberLunes?"*  
> **Agente IA:** *"Para eventos de alto tráfico como CyberLunes o Black Friday, los tiempos de entrega se extenderán hasta +48 horas hábiles adicionales."*  
> **Fuentes:** `MOP-2026-V5-COP (Página 1)`

### ❓ Pregunta 2 (Consultas Financieras)
> **Usuario:** *"¿Qué valor hubo en ventas en el mes de mayo?"*  
> **Agente IA:** *"El valor de las ventas brutas en el mes de mayo fue de $2.100.000.000 COP."*  
> **Fuentes:** `MOP-2026-V5-COP (Página 2)`

### ❓ Pregunta 3 (Control de Alucinaciones / Fallback)
> **Usuario:** *"¿Cuánto son las ganancias del mes de mayo del 2026?"*  
> **Agente IA:** *"No encontré esta información en los documentos operativos disponibles. Te sugiero consultar con el área de Finanzas."*  
> **Fuentes:** `MOP-2026-V5-COP (Página 2)`

---

## 📸 Vista Previa del Sistema

| Interfaz y Búsqueda Semántica | Desglose de Respuestas y Métricas | Registro de Ejecución y Terminal |
| :---: | :---: | :---: |
| ![Interfaz](docs/evidencia_interfaz_y_politicas.png) | ![Respuestas](docs/evidencia_respuesta_ventas.png) | ![Logs](docs/evidencia_logs_y_respuestas.png) |

---

## 🛠️ Tecnologías Utilizadas

* **Lenguaje:** Python 3.10+
* **Framework Web:** Streamlit
* **Modelo LLM:** Google Gemini API (`gemini-flash-lite-latest`)
* **Framework de IA:** LangChain (`langchain-google-genai`, `langchain-chroma`, `langchain-huggingface`)
* **Embeddings:** `sentence-transformers/all-MiniLM-L6-v2` (Modelo multilingüe local)
* **Base de Datos Vectorial:** ChromaDB
* **Procesamiento de Documentos:** PyPDF
* **Entorno & Despliegue:** Streamlit Community Cloud & GitHub CI/CD

---

## 🏗️ Arquitectura del Sistema (RAG Pipeline)

1. **Ingestión y Carga:** Carga de documentos operativos en formato PDF (`data/`).
2. **Chunking & Indexación:** Segmentación de texto en fragmentos optimizados (*chunks*) con solapamiento (*overlap*).
3. **Embeddings Locales:** Generación de vectores densos utilizando HuggingFace Transformers.
4. **Almacenamiento Vectorial:** Persistencia de embeddings y metadatos en **ChromaDB**.
5. **Recuperación Semántica:** Búsqueda por similitud de coseno para extraer los fragmentos más relevantes ante la consulta del usuario.
6. **Generación Aumentada (LLM):** Inyección del contexto recuperado en el Prompt de **Google Gemini** obligando al modelo a responder estrictamente con base en las fuentes o activar una respuesta de reserva (*fallback*).

---

## 📂 Estructura del Proyecto

```text
Alura-Agente-IA/
├── data/                      # Documentos PDF a indexar
├── docs/                      # Evidencias multimedia de ejecución en la nube
├── src/
│   ├── loader.py              # Carga y segmentación de documentos PDF
│   ├── vectorstore.py         # Creación y gestión de la base ChromaDB
│   ├── retriever.py           # Recuperación de contexto semántico
│   └── generator.py           # Integración con Google Gemini (RAG)
├── app.py                     # Interfaz web principal con Streamlit
├── chroma_db/                 # Base de datos vectorial persistente
├── .env.example               # Plantilla de variables de entorno
├── requirements.txt           # Dependencias del proyecto
└── README.md                  # Documentación oficial
```
# 🚀 Instalación y Ejecución Local
### 1. Clonar el repositorio
```
Bash

git clone [https://github.com/EdsonCasta/Alura-Agente-IA.git](https://github.com/EdsonCasta/Alura-Agente-IA.git)
cd Alura-Agente-IA
```
### 2. Crear y activar entorno virtual
```
Bash

# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar dependencias
```
Bash

pip install -r requirements.txt
```
### 4. Configurar variables de entorno
Crea un archivo `.env` en la raíz basado en `.env.example`:
```
Fragmento de código

GEMINI_API_KEY=tu_api_key_de_google_gemini
```

### 5. Ejecutar la aplicación
```
Bash

streamlit run app.py
```

# 📊 Registro de Ejecución, Trazabilidad
El sistema cuenta con un pipeline de observabilidad y auditoría desplegado en producción:

Centralización de Logs: Streamlit Cloud registra la salida estándar (`stdout/stderr`), capturando marcas de tiempo, descargas de modelos y búsquedas vectoriales en tiempo real.

Control de Calidad: Implementación de métricas de retroalimentación de usuario (👍 / 👎) integradas en el estado de la sesión (`st.session_state`).

CI/CD Continuo: Integración directa con GitHub; cada actualización en la rama `main` realiza la construcción y despliegue automático del agente.

# ✒️ Autor
Edson Castañeda – Software Developer – GitHub
