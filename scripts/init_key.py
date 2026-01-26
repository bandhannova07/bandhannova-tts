
import os
import sys

# Add parent directory to path so we can import api_keys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api_keys import create_api_key, _load_keys

def init_key():
    print("Checking for existing API keys...")
    keys = _load_keys()
    if keys:
        print(f"Found {len(keys)} existing keys.")
        for k, v in keys.items():
            print(f"Key ({v.get('label', 'unknown')}): {k}")
    else:
        print("No keys found. Generating default 'admin' key...")
        key = create_api_key(label="admin")
        print("\nSUCCESS! New API Key generated:")
        print(f"Key: {key}")
        print("\nPlease add this key to your client environment variables as 'TTS_API_KEY' or use it in the 'X-API-Key' header.")

if __name__ == "__main__":
    init_key()
