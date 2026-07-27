import os
import uuid

import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = (os.getenv("SUPABASE_URL") or "").rstrip("/")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
BUCKET = "produtos"


class StorageService:
    """Envia e remove fotos de produtos no bucket público do Supabase Storage."""

    def __init__(self):
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("SUPABASE_URL/SUPABASE_KEY não encontrados no .env")
        self._headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}

    def enviar_foto(self, conteudo: bytes, content_type: str = "image/jpeg") -> str:
        caminho = f"{uuid.uuid4().hex}.jpg"
        resposta = requests.post(
            f"{SUPABASE_URL}/storage/v1/object/{BUCKET}/{caminho}",
            headers={**self._headers, "Content-Type": content_type},
            data=conteudo,
            timeout=30,
        )
        resposta.raise_for_status()
        return f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET}/{caminho}"

    def excluir_foto(self, url: str | None):
        if not url or f"/object/public/{BUCKET}/" not in url:
            return
        caminho = url.split(f"/object/public/{BUCKET}/")[-1]
        requests.delete(
            f"{SUPABASE_URL}/storage/v1/object/{BUCKET}/{caminho}",
            headers=self._headers,
            timeout=30,
        )
