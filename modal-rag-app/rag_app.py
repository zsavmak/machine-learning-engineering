import modal

image = modal.Image.debian_slim(python_version="3.11").apt_install("libmagic1").pip_install(
    "langchain-community",
    "faiss-gpu-cu12",
    "langchain-huggingface",
    "fastapi[standard]",
    "pydantic",
    "starlette",
    "sentence-transformers",
    "unstructured[md]",
    "python-magic",
    "numpy",
)

app = modal.App(
    name="mcp-retrieval-api",
    image=image,
)

source_volume = modal.Volume.from_name("source-volume")
vector_store_volume = modal.Volume.from_name("vector-store-volume")
model_cache_volume = modal.Volume.from_name("model-cache-volume")

VECTOR_STORE_ROOT = "/vector_store"
SOURCE_ROOT = "/source"
CACHE_PATH = "/model_cache"


@app.function(
    volumes={
        SOURCE_ROOT: source_volume,
        VECTOR_STORE_ROOT: vector_store_volume,
        CACHE_PATH: model_cache_volume,
    },
    gpu="A100-40GB",
    cpu=4,
    timeout=300,
)
def create_index(db_name: str):
    from pathlib import Path
    from langchain_community.document_loaders import DirectoryLoader
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain_community.vectorstores import FAISS

    print(f"[create_index] Starting indexing for database: {db_name}")
    print("[create_index] Loading embedding model from cache...")
    embeddings = HuggingFaceEmbeddings(
        model_name="Qwen/Qwen3-Embedding-8B",
        cache_folder=CACHE_PATH,
        model_kwargs={"device": "cuda"}
    )
    print("[create_index] Model loaded.")

    data_path = Path(SOURCE_ROOT) / db_name
    vector_store_path = Path(VECTOR_STORE_ROOT) / db_name

    if not data_path.exists():
        raise FileNotFoundError(f"Source directory '{data_path}' not found in Volume.")

    loader = DirectoryLoader(str(data_path), glob="**/*.md", show_progress=True, use_multithreading=True)
    documents = loader.load()

    if not documents:
        print(f"No documents found in {data_path}. Aborting indexing.")
        return

    print(f"[create_index] Loaded {len(documents)} documents. Splitting and embedding...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = text_splitter.split_documents(documents)

    vector_store = FAISS.from_documents(docs, embeddings)
    
    print(f"[create_index] Saving index to {vector_store_path}...")
    vector_store.save_local(folder_path=str(vector_store_path))
    vector_store_volume.commit()
    print(f"[create_index] Indexing for {db_name} complete.")


@app.function(
    volumes={
        VECTOR_STORE_ROOT: vector_store_volume,
        CACHE_PATH: model_cache_volume,
    },
    scaledown_window=2,
)
@modal.asgi_app(requires_proxy_auth=True)
def fastapi_app():
    from fastapi import FastAPI, Request, HTTPException
    from fastapi.responses import JSONResponse
    from pathlib import Path
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain_community.vectorstores import FAISS

    web_app = FastAPI()

    @web_app.post("/databases/{db_name}")
    def start_indexing_job(db_name: str):
        create_index.spawn(db_name)
        return {"message": f"Indexing job for database '{db_name}' has been started."}

    @web_app.get("/databases")
    def list_databases():
        db_list = [p.name for p in Path(VECTOR_STORE_ROOT).iterdir() if p.is_dir()]
        return {"databases": db_list}

    @web_app.post("/query/{db_name}")
    def query(db_name: str, request: dict):
        query_text = request.get("query")
        k = request.get("k", 4)
        if not query_text:
            return JSONResponse({"error": "Query not provided"}, status_code=400)

        print("[API] Loading embedding model from cache...")
        embeddings = HuggingFaceEmbeddings(
            model_name="Qwen/Qwen3-Embedding-8B",
            cache_folder=CACHE_PATH
        )
        print("[API] Model loaded.")

        vector_store_path = str(Path(VECTOR_STORE_ROOT) / db_name)
        if not (Path(vector_store_path) / "index.faiss").exists():
            raise HTTPException(status_code=404, detail=f"Database '{db_name}' not found or not indexed.")

        vector_store = FAISS.load_local(
            folder_path=vector_store_path, embeddings=embeddings, allow_dangerous_deserialization=True
        )

        retriever = vector_store.as_retriever(search_kwargs={"k": k})
        documents = retriever.get_relevant_documents(query_text)
        
        return [{"page_content": doc.page_content, "metadata": doc.metadata} for doc in documents]

    return web_app