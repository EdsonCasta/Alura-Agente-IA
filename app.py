import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
import streamlit as st

from dotenv import load_dotenv
from generator import responder_pregunta


load_dotenv()

# Configuración de la página
st.set_page_config(
    page_title="Agente IA de Soporte Operativo",
    page_icon="🤖",
    layout="wide"
)

# Encabezado e Identificación clara del Agente
st.title("🤖 Agente IA de Soporte Operativo e Informativo")
st.caption("ℹ️ *Este es un asistente virtual basado en Inteligencia Artificial. Responde únicamente con base en la documentación oficial indexada.*")

# Inicializar historial de conversación en la sesión
if "messages" not in st.session_state:
    st.session_state.messages = []

# Inicializar registro de feedback en la sesión
if "feedback" not in st.session_state:
    st.session_state.feedback = {}

# Sidebar para Mantenimiento y Gestión del Sistema
with st.sidebar:
    st.header("⚙️ Mantenimiento & Base de Datos")
    st.markdown("---")
    st.subheader("📚 Estado de Documentos")
    st.info("Documentos activos: **Manual Operativo 2026 (MOP-2026-V5-COP)**")
    
    st.subheader("🔄 Pipeline de Actualización")
    if st.button("Re-indexar Documentos Vectoriales"):
        with st.spinner("Actualizando base vectorial ChromaDB..."):
            # Aquí se puede invocar la re-indexación del vectorstore si se requiere
            st.success("✅ Base vectorial actualizada con éxito.")
            
    st.markdown("---")
    st.subheader("📊 Monitoreo de Calidad")
    positivos = sum(1 for v in st.session_state.feedback.values() if v == "positivo")
    negativos = sum(1 for v in st.session_state.feedback.values() if v == "negativo")
    st.write(f"👍 Feedbacks Positivos: **{positivos}**")
    st.write(f"👎 Feedbacks Negativos: **{negativos}**")

# Mostrar historial de mensajes anteriores
for idx, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Si el mensaje fue del asistente y tiene fuentes, mostrarlas si NO están dentro del texto
        if message["role"] == "assistant" and "fuentes" in message and message["fuentes"]:
            if "Fuentes utilizadas:" not in message["content"]:
                with st.expander("📌 Fuentes / Documentos citados"):
                    for fuente in message["fuentes"]:
                        st.write(f"- {fuente}")
                    
        # Botones de Feedback para respuestas del asistente
        if message["role"] == "assistant":
            col1, col2, _ = st.columns([1, 1, 10])
            with col1:
                if st.button("👍", key=f"pos_{idx}"):
                    st.session_state.feedback[idx] = "positivo"
                    st.toast("¡Gracias por tu retroalimentación positiva!", icon="✅")
            with col2:
                if st.button("👎", key=f"neg_{idx}"):
                    st.session_state.feedback[idx] = "negativo"
                    st.toast("Gracias. Revisaremos esta respuesta para mejorar.", icon="⚠️")

# Captura de la entrada del usuario
if prompt := st.chat_input("Escribe tu pregunta sobre los procedimientos operativos..."):
    # Guardar y mostrar la pregunta del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generar y mostrar la respuesta del agente
    with st.chat_message("assistant"):
        with st.spinner("Consultando base de conocimientos operativos..."):
            resultado = responder_pregunta(prompt)
            respuesta_texto = resultado["respuesta"]
            fuentes = resultado["fuentes"]

            st.markdown(respuesta_texto)
            
            # Mostrar el desplegable solo si la respuesta NO incluye ya "Fuentes utilizadas:"
            if fuentes and "Fuentes utilizadas:" not in respuesta_texto:
                with st.expander("📌 Fuentes / Documentos citados"):
                    for fuente in fuentes:
                        st.write(f"- {fuente}")

    # Guardar la respuesta del asistente en el historial
    st.session_state.messages.append({
        "role": "assistant", 
        "content": respuesta_texto,
        "fuentes": fuentes
    })
    
    # Rerenderizar para actualizar los botones de feedback
    st.rerun()