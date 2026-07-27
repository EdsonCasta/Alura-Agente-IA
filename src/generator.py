import os
from typing import Dict, Any
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from retriever import recuperar_contexto

load_dotenv()

def obtener_llm():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(" No se encontró GEMINI_API_KEY en el archivo .env")
    
    return ChatGoogleGenerativeAI(
        model="gemini-flash-lite-latest",
        temperature=0.0,
        google_api_key=api_key
    )

PROMPT_RAG = ChatPromptTemplate.from_messages([
    ("system", """Eres un asistente virtual de soporte operativo e informativo para colaboradores.
Tu objetivo es responder a la pregunta del usuario utilizando UNICAMENTE el contexto proporcionado.

REGLAS DE RESPUESTA:
1. Usa SOLAMENTE la informacion del 'CONTEXTO RECUPERADO'. No inventes ni asumas datos externos.
2. Si el contexto NO contiene la informacion suficiente para responder con certeza, responde exactamente:
   "No encontre esta informacion en los documentos operativos disponibles." e indica al usuario que puede consultar con el área encargada (Operaciones, Atención al Cliente, Logística o Finanzas según corresponda).
3. Siempre incluye las citas de las fuentes utilizadas al final de tu respuesta de forma clara (Codigo de documento y página).
4. Manten un tono profesional, claro y directo.
"""),
    ("human", """CONTEXTO RECUPERADO:
{contexto}

PREGUNTA DEL USUARIO:
{pregunta}

RESPUESTA:"""),
])


def responder_pregunta(
    pregunta: str, 
    umbral_distancia: float = 1.6
) -> Dict[str, Any]:
    """
    Etapa 5: Generacion de respuesta con control de alucinaciones y fallback.
    """
    resultado_retrieval = recuperar_contexto(query=pregunta, k_inicial=5, top_k_final=3)
    documentos = resultado_retrieval["documentos"]
    contexto_texto = resultado_retrieval["contexto_texto"]

    if not documentos or (documentos[0]["distancia"] > umbral_distancia):
        return {
            "respuesta": (
                " **Informacion no disponible:**\n"
                "No encontre esta informacion en los documentos operativos disponibles.\n\n"
                " **Sugerencia:** Por favor ponte en contacto con el area de **Atencion al Cliente / Operaciones** "
                "o escala la solicitud con tu supervisor encargado."
            ),
            "fuentes": [],
            "relevancia_alta": False
        }

    llm = obtener_llm()
    chain = PROMPT_RAG | llm
    
    respuesta_llm = chain.invoke({
        "contexto": contexto_texto,
        "pregunta": pregunta
    })

    texto_raw = respuesta_llm.content
    if isinstance(texto_raw, list):
        partes = []
        for bloque in texto_raw:
            if isinstance(bloque, dict) and "text" in bloque:
                partes.append(bloque["text"])
            elif hasattr(bloque, "text"):
                partes.append(bloque.text)
            else:
                partes.append(str(bloque))
        texto_respuesta = "\n".join(partes).strip()
    else:
        texto_respuesta = str(texto_raw).strip()

    fuentes = []
    for doc in documentos:
        meta = doc["metadata"]
        codigo = meta.get("documento_codigo", "Doc")
        pagina = meta.get("page_label", meta.get("page", "N/A"))
        fuente_str = f"{codigo} (Pág. {pagina})"
        if fuente_str not in fuentes:
            fuentes.append(fuente_str)

    return {
        "respuesta": texto_respuesta,
        "fuentes": fuentes,
        "relevancia_alta": True
    }

if __name__ == "__main__":
    print(" --- PRUEBA 1: Pregunta dentro del documento ---")
    p1 = "¿Cuales son los tiempos de entrega para compras en CyberLunes o eventos de alto trafico?"
    res1 = responder_pregunta(p1)
    print(f"Pregunta: {p1}\n")
    print(f"Respuesta:\n{res1['respuesta']}\n")
    print(f"Fuentes: {res1['fuentes']}\n")
    print("="*60)

    print("\n --- PRUEBA 2: Pregunta fuera del alcance (Fallback) ---")
    p2 = "¿Cual es el menu del almuerzo en la cafeteria principal?"
    res2 = responder_pregunta(p2)
    print(f"Pregunta: {p2}\n")
    print(f"Respuesta:\n{res2['respuesta']}")