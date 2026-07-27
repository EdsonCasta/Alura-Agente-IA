import os
import re
import sys
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Configurar salida a UTF-8 para consola Windows
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_PDF_PATH = BASE_DIR / "data" / "manual_operativo_techmarket_cop.pdf"

def limpiar_texto(texto: str) -> str:
    """
    Punto 2 de Trello: Limpieza básica de ruido en el texto extraído.
    """
    # Reemplaza múltiples espacios en blanco y saltos de línea excesivos
    texto = re.sub(r'[ \t]+', ' ', texto)
    texto = re.sub(r'\n\s*\n', '\n\n', texto)
    return texto.strip()

def cargar_y_procesar_pdf(pdf_path: Path = DEFAULT_PDF_PATH):
    """
    Procesa el PDF aplicando Extracción, Limpieza, Chunking y Metadatos.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"No se encontró el archivo PDF en la ruta: {pdf_path}")

    print(f" Cargando documento: {pdf_path.name}...")
    loader = PyPDFLoader(str(pdf_path))
    documentos = loader.load()

    print(f" Páginas cargadas: {len(documentos)}")

    # 1 y 2. Limpieza de texto en cada página cargada
    for doc in documentos:
        doc.page_content = limpiar_texto(doc.page_content)

    # 3. Chunking (División en fragmentos)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=100,
        length_function=len
    )
    chunks = text_splitter.split_documents(documentos)

    # 4. Atribución de Metadatos globales y específicos
    for idx, chunk in enumerate(chunks):
        chunk.metadata.update({
            "empresa": "TechMarket Colombia S.A.S.",
            "documento_codigo": "MOP-2026-V5-COP",
            "fecha_actualizacion": "Julio 2026",
            "moneda": "COP",
            "chunk_id": idx + 1
        })

    print(f" Texto limpio y dividido en {len(chunks)} fragmentos con metadatos completos.")
    return chunks

if __name__ == "__main__":
    fragmentos = cargar_y_procesar_pdf()
    print("\n Ejemplo del primer fragmento y sus metadatos:")
    print("=" * 60)
    print("CONTENIDO:")
    print(fragmentos[0].page_content)
    print("\nMETADATOS ASOCIADOS:")
    print(fragmentos[0].metadata)
    print("=" * 60)