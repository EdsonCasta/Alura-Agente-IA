import os
from typing import List, Dict, Any, Optional
from langchain_chroma import Chroma
from langchain_core.documents import Document
from vectorstore import obtener_modelo_embeddings

CHROMA_PATH = "chroma_db"

def obtener_vectorstore() -> Chroma:
    """Carga la base de datos vectorial Chroma existente."""
    if not os.path.exists(CHROMA_PATH):
        raise FileNotFoundError(f" La base de datos {CHROMA_PATH} no existe. Ejecuta primero src/vectorstore.py")
    
    embeddings = obtener_modelo_embeddings()
    return Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings
    )

def recuperar_contexto(
    query: str, 
    k_inicial: int = 10, 
    top_k_final: int = 3,
    filtro_metadatos: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Capa de Recuperación completa:
    1. Transformación de la pregunta en embedding (Automático por Chroma + Embeddings)
    2. Búsqueda semántica
    3. Filtrado por metadatos (opcional)
    4. Reclasificación (Reranking/Filtering por relevancia)
    5. Ensamblaje del contexto
    """
    vectorstore = obtener_vectorstore()
    
    # Fases 1, 2 y 3: Búsqueda Vectorial Amplia + Filtrado por Metadatos
    print(f" Realizando búsqueda vectorial para: '{query}'...")
    
    # Chroma busca k_inicial candidatos
    resultados_con_score = vectorstore.similarity_search_with_score(
        query=query,
        k=k_inicial,
        filter=filtro_metadatos
    )
    
    if not resultados_con_score:
        return {
            "contexto_texto": "No se encontró información relevante en los documentos.",
            "documentos": []
        }

    # Fase 4: Reclasificación (Reranking)
    # Ordenamos por menor distancia (mayor similitud) y tomamos los top_k_final más útiles
    candidatos_reordenados = sorted(resultados_con_score, key=lambda x: x[1])[:top_k_final]

    # Fase 5: Ensamblaje del Contexto
    bloques_contexto = []
    documentos_recuperados = []

    for i, (doc, score) in enumerate(candidatos_reordenados, 1):
        origen = doc.metadata.get("source", "Documento desconocido")
        pagina = doc.metadata.get("page_label", doc.metadata.get("page", "N/A"))
        codigo = doc.metadata.get("documento_codigo", "N/A")
        
        # Estructuramos cada bloque con sus metadatos visibles para la cita
        bloque = (
            f"--- FUENTE [{i}] ---\n"
            f"Documento: {codigo} (Página {pagina})\n"
            f"Contenido:\n{doc.page_content.strip()}\n"
        )
        bloques_contexto.append(bloque)
        
        documentos_recuperados.append({
            "contenido": doc.page_content,
            "metadata": doc.metadata,
            "distancia": score
        })

    contexto_final = "\n".join(bloques_contexto)

    return {
        "contexto_texto": contexto_final,
        "documentos": documentos_recuperados
    }


if __name__ == "__main__":
    # Prueba del pipeline de recuperación
    pregunta_prueba = "¿Cuáles son los tiempos de entrega para compras en CyberLunes o eventos de alto tráfico?"
    
    resultado = recuperar_contexto(
        query=pregunta_prueba,
        k_inicial=5,
        top_k_final=2
    )

    print("\n" + "="*60)
    print(" CONTEXTO ENSAMBLADO PARA EL LLM:")
    print("="*60)
    print(resultado["contexto_texto"])