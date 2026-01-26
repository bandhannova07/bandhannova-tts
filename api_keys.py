"""
Simple API key management for TTS service.
"""
import json
import os
import secrets
import threading
from datetime import datetime, timezone

_KEYS_FILE = os.path.join(os.path.dirname(__file__), "api_keys.json")
_LOCK = threading.Lock()


def _load_keys():
    if not os.path.exists(_KEYS_FILE):
        return {}
    with open(_KEYS_FILE, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _save_keys(keys):
    with open(_KEYS_FILE, "w", encoding="utf-8") as handle:
        json.dump(keys, handle, indent=2, sort_keys=True)


def create_api_key(label="public"):
    with _LOCK:
        keys = _load_keys()
        key = secrets.token_urlsafe(32)
        keys[key] = {
            "label": label,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        _save_keys(keys)
        return key


def is_valid_key(key):
    if not key:
        return False
    with _LOCK:
        keys = _load_keys()
        return key in keys

def get_first_key():
    with _LOCK:
        keys = _load_keys()
        if keys:
            return list(keys.keys())[0]
    return None
