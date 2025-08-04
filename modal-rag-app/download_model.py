
import modal

image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "langchain-huggingface",
    "sentence-transformers",
)

app = modal.App(
    name="model-downloader",
    image=image,
)

model_cache_volume = modal.Volume.from_name("model-cache-volume")
CACHE_PATH = "/model_cache"

@app.function(
    volumes={CACHE_PATH: model_cache_volume}
)
def download_model():
    from langchain_huggingface import HuggingFaceEmbeddings

    print("Downloading and caching embedding model...")
    
    # This function will download the model from Hugging Face and
    # the library will automatically save it to the cache directory
    # specified by the HF_HOME environment variable.
    HuggingFaceEmbeddings(
        model_name="Qwen/Qwen3-Embedding-8B",
        cache_folder=CACHE_PATH
    )
    
    print("Model downloaded and cached successfully.")
    model_cache_volume.commit()

@app.local_entrypoint()
def main():
    download_model.remote()
