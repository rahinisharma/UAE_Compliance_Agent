import os
import time
import shutil
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_cohere import CohereEmbeddings
from langchain_chroma import Chroma

load_dotenv()

# 1. Initialize Cohere
embeddings = CohereEmbeddings(
    cohere_api_key=os.getenv("COHERE_API_KEY"), 
    model="embed-english-v3.0"
)

def run_ingestion():
    # --- CLEANUP: Delete old DB folder to start fresh ---
    if os.path.exists("./cohere_db"):
        print("🧹 Cleaning up old database folder...")
        shutil.rmtree("./cohere_db")

    pdf_configs = [
        {"path": "data/01_corporate_tax/Federal-Decree-Law-No.-47-of-2022-EN.pdf", "label": "Corporate Tax"},
        {"path": "data/02_data_privacy/Federal Decree by Law No. (45) of 2021 Concerning the Protection of Personal Data.pdf", "label": "Data Privacy"},
        {"path": "data/03_nesa_compliance/UAE Information Assurance Regulation v1 1 pdf.pdf", "label": "NESA Compliance"},
        {"path": "data/04_ai_charter/UAEAI-Methaq-Jul-EN.pdf", "label": "AI Charter"}
    ]
    
    all_chunks = []
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    
    print("--- 📥 Phase 1: Loading PDFs ---")
    for config in pdf_configs:
        if os.path.exists(config["path"]):
            loader = PyPDFLoader(config["path"])
            docs = loader.load()
            all_chunks.extend(text_splitter.split_documents(docs))
            print(f"✅ Loaded {config['label']}")

    print(f"\n🔢 Total chunks: {len(all_chunks)}")
    
    # --- PHASE 2: Indexing with Rate Limit Protection ---
    print("--- 🚀 Phase 2: Safe Indexing (Staying under 100k TPM) ---")
    
    # Create the empty DB
    vector_db = Chroma(embedding_function=embeddings, persist_directory="./cohere_db")
    
    batch_size = 25  # Small enough to stay under limits
    for i in range(0, len(all_chunks), batch_size):
        batch = all_chunks[i : i + batch_size]
        print(f"📦 Indexing batch {i//batch_size + 1}... ({i}/{len(all_chunks)})")
        
        try:
            vector_db.add_documents(batch)
            # 10 second wait is the "sweet spot" for Cohere Trial keys
            time.sleep(10) 
        except Exception as e:
            print(f"⚠️ Limit hit or Error: {e}")
            print("⏳ Cooling down for 40 seconds...")
            time.sleep(40)
            vector_db.add_documents(batch) # Retry

    print("\n✅ SUCCESS: UAE Legal Database is fully built!")

if __name__ == "__main__":
    run_ingestion()