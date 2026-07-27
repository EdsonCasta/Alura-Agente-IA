import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
import streamlit as st

from dotenv import load_dotenv
from generator import responder_pregunta


load_dotenv()

st.set_page_config(
    page_title="Agente IA de Soporte Operativo",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Agente IA de Soporte Operativo e Informativo")
st.caption("ℹ️ *Este es un asistente virtual basado en Inteligencia Artificial. Responde únicamente con base en la documentación oficial indexada.*")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "feedback" not in st.session_state:
    st.session_state.feedback = {}

with st.sidebar:
    st.header("⚙️ Mantenimiento & Base de Datos")
    st.markdown("---")
    st.subheader("📚 Estado de Documentos")
    st.info("Documentos activos: **Manual Operativo 2026 (MOP-2026-V5-COP)**")
    
    st.subheader("🔄 Pipeline de Actualización")
    if st.button("Re-indexar Documentos Vectoriales"):
        with st.spinner("Actualizando base vectorial ChromaDB..."):
            st.success("✅ Base vectorial actualizada con éxito.")
            
    st.markdown("---")
    st.subheader("📊 Monitoreo de Calidad")
    positivos = sum(1 for v in st.session_state.feedback.values() if v == "positivo")
    negativos = sum(1 for v in st.session_state.feedback.values() if v == "negativo")
    st.write(f"👍 Feedbacks Positivos: **{positivos}**")
    st.write(f"👎 Feedbacks Negativos: **{negativos}**")

for idx, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        if message["role"] == "assistant" and "fuentes" in message and message["fuentes"]:
            if "Fuentes utilizadas:" not in message["content"]:
                with st.expander("📌 Fuentes / Documentos citados"):
                    for fuente in message["fuentes"]:
                        st.write(f"- {fuente}")
                    
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

if prompt := st.chat_input("Escribe tu pregunta sobre los procedimientos operativos..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Consultando base de conocimientos operativos..."):
            resultado = responder_pregunta(prompt)
            respuesta_texto = resultado["respuesta"]
            fuentes = resultado["fuentes"]

            st.markdown(respuesta_texto)
            
            if fuentes and "Fuentes utilizadas:" not in respuesta_texto:
                with st.expander("📌 Fuentes / Documentos citados"):
                    for fuente in fuentes:
                        st.write(f"- {fuente}")

    st.session_state.messages.append({
        "role": "assistant", 
        "content": respuesta_texto,
        "fuentes": fuentes
    })
    
    st.rerun()