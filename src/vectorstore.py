import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from src.loader import cargar_y_procesar_pdf

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()
CHROMA_PATH = BASE_DIR / "chroma_db"

def obtener_modelo_embeddings():
    """
    Modelo de Embeddings multilingüe corriendo 100% local.
    """
    print(" Cargando modelo de embeddings local (HuggingFace)...")
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def crear_o_cargar_vectorstore():
    """
    2 y 3. Almacenamiento e Indexación de Chunks + Metadatos
    """
    embeddings = obtener_modelo_embeddings()

    if os.path.exists(CHROMA_PATH) and os.listdir(CHROMA_PATH):
        print(f" Cargando VectorStore existente desde: {CHROMA_PATH}...")
        vectorstore = Chroma(
            persist_directory=str(CHROMA_PATH),
            embedding_function=embeddings
        )
    else:
        print(" Creando nueva base de datos vectorial en ChromaDB...")
        chunks = cargar_y_procesar_pdf()
        
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=str(CHROMA_PATH)
        )
        print(f" VectorStore indexado con éxito en {CHROMA_PATH}!")

    return vectorstore

if __name__ == "__main__":
    vectorstore = crear_o_cargar_vectorstore()

    query = "¿Cuáles son los tiempos y costos de envío?"
    print(f"\n Búsqueda semántica para: '{query}'")
    
    resultados = vectorstore.similarity_search(query, k=2)

    print("\n Resultados más relevantes:")
    print("=" * 60)
    for idx, doc in enumerate(resultados):
        print(f"--- Resultado {idx + 1} ---")
        print(f"Contenido: {doc.page_content[:250]}...")
        print(f"Metadatos: {doc.metadata}")
        print("=" * 60)