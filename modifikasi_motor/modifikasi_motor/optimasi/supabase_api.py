"""
Klien kecil untuk Supabase Data API (PostgREST) memakai API key.

Memakai urllib bawaan Python supaya tidak butuh library tambahan dan cocok dengan format key baru
(sb_publishable_... dan sb_secret_...). Key dikirim lewat header "apikey" saja, bukan "Authorization".
"""
import json
import urllib.error
import urllib.parse
import urllib.request


class SupabaseAPIError(Exception):
    """Dilempar kalau permintaan ke Supabase gagal."""


def ambil_tabel(url_proyek, api_key, tabel, batas=10, timeout=10):
    """GET {url_proyek}/rest/v1/{tabel}?select=*&limit={batas} -> list of dict."""
    alamat = f"{url_proyek.rstrip('/')}/rest/v1/{urllib.parse.quote(tabel)}?select=*&limit={int(batas)}"
    req = urllib.request.Request(alamat, headers={"apikey": api_key, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        isi = e.read().decode("utf-8", errors="replace")[:300]
        raise SupabaseAPIError(f"HTTP {e.code}: {isi}") from e
    except urllib.error.URLError as e:
        raise SupabaseAPIError(f"Gagal terhubung ke Supabase: {e.reason}") from e
