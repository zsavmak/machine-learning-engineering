import os
import requests
import argparse

API_BASE_URL = "https://zsavmak--mcp-retrieval-api-fastapi-app.modal.run"

def trigger_indexing(db_name: str):
    modal_key = "wk-xIVfesg3UV1l0uWi9bGxZP"
    modal_secret = "ws-k0nzSyMwjEBMAQxMlfvnLa"

    if not modal_key or not modal_secret:
        print("Error: MODAL_KEY and MODAL_SECRET environment variables must be set.")
        print("You can get them from https://modal.com/keys")
        return

    headers = {
        "Modal-Key": modal_key,
        "Modal-Secret": modal_secret,
    }

    url = f"{API_BASE_URL}/databases/{db_name}"

    print(f"Sending indexing request for database '{db_name}' to URL: {url}")

    try:
        response = requests.post(url, headers=headers, timeout=300)

        if response.status_code == 200:
            print("\033[92mSuccess!\033[0m")
            print(f"Server response: {response.json()}")
            print("Indexing process started in the background on the server.")
        else:
            print(f"\033[91mError!\033[0m")
            print(f"Status code: {response.status_code}")
            print(f"Server response: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"\033[91mConnection Error!\033[0m")
        print(f"Failed to connect to the server: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Triggers the indexing process for a database on the MCP server."
    )
    parser.add_argument(
        "db_name",
        type=str,
        help="The name of the database to be indexed (e.g., 'docs_db')."
    )
    args = parser.parse_args()

    trigger_indexing(args.db_name)