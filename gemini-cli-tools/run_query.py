import requests
import argparse
import json

def call_retrieval_api(db_name: str, query: str, k: int):
    url = f"https://zsavmak--mcp-retrieval-api-fastapi-app.modal.run/query/{db_name}"
    
    headers = {
        "Content-Type": "application/json",
        "Modal-Key": "wk-msd6a3Fhz4oNkeVU8Swvw4", 
        "Modal-Secret": "ws-HcHvExxOU5rDYlm19RETim" 
    }
    
    payload = {
        "query": query,
        "k": k
    }
    
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("db_name", type=str)
    parser.add_argument("query", type=str)
    parser.add_argument("--k", type=int, default=4)
    
    args = parser.parse_args()
    
    call_retrieval_api(args.db_name, args.query, args.k)
