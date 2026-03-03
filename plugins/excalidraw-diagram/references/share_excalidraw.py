#!/usr/bin/env python3
"""Upload .excalidraw file to excalidraw.com and return a shareable URL.

Uses the same E2E encryption format as excalidraw.com's native sharing:
- AES-GCM encryption with a random 128-bit key
- zlib compression (pako-compatible)
- Key stays in the URL hash fragment (never sent to server)
"""

import base64
import json
import os
import sys
import urllib.request
import zlib
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def share(filepath: str) -> str:
    """Upload an .excalidraw file to excalidraw.com, return shareable URL."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    with open(path) as f:
        data = json.load(f)

    # Serialize and compress
    plaintext = json.dumps(data).encode("utf-8")
    compressed = zlib.compress(plaintext)

    # Generate encryption materials
    key = os.urandom(16)  # 128-bit AES key
    iv = os.urandom(12)   # 96-bit GCM nonce

    # Encrypt with AES-GCM
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(iv, compressed, None)

    # Build v2 binary payload: [metadata UTF-8] [0x00] [IV 12B] [ciphertext]
    metadata = json.dumps({
        "version": 2,
        "compression": "pako@1",
        "encryption": "AES-GCM",
    }).encode("utf-8")

    payload = metadata + b"\x00" + iv + ciphertext

    # Upload to excalidraw store
    req = urllib.request.Request(
        "https://json.excalidraw.com/api/v2/post/",
        data=payload,
        headers={"Content-Type": "application/octet-stream"},
        method="POST",
    )

    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())

    doc_id = result["id"]

    # Encode key as base64url (no padding) — stays in URL hash, never sent to server
    key_b64 = base64.urlsafe_b64encode(key).rstrip(b"=").decode("ascii")

    return f"https://excalidraw.com/#json={doc_id},{key_b64}"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <file.excalidraw>", file=sys.stderr)
        sys.exit(1)

    url = share(sys.argv[1])
    print(url)
