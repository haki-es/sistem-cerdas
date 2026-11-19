"""
Penjelasan hasil optimasi memakai Gemini API (REST, tanpa library tambahan).
API key dikirim lewat header "x-goog-api-key", bukan di URL.
"""
import json
import urllib.error
import urllib.request

ALAMAT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
# Dicoba berurutan kalau model utama tidak ditemukan (HTTP 404).
MODEL_CADANGAN = ["gemini-3.5-flash", "gemini-3-flash-preview", "gemini-2.5-flash"]


class GeminiError(Exception):
    """Dilempar kalau permintaan ke Gemini gagal."""


def buat_prompt(h):
    terpilih = "; ".join(
        f'{p["nama"]} (biaya Rp {p["biaya"]} jt, performa {p["nilai"]})' for p in h.part_terpilih
    ) or "tidak ada part yang muat dalam batas"
    riw = h.riwayat_fitness or []
    awal, akhir = (riw[0], riw[-1]) if riw else (0, 0)
    mulai_stabil = next((i + 1 for i, v in enumerate(riw) if v == akhir), 0)
    bf = (
        f"Optimum brute force = {h.optimum_bf}; GA {'menemukan' if h.cocok_bf else 'belum menemukan'} optimum."
        if h.optimum_bf is not None else "Perbandingan brute force tidak dijalankan."
    )
    bobot = f" Batas tambahan bobot {h.batas_bobot} kg." if h.batas_bobot is not None else ""
    return f"""Kamu asisten dosen mata kuliah Sistem Cerdas. Jelaskan hasil optimasi modifikasi motor sport berikut, yang dicari dengan algoritma genetika (GA), untuk mahasiswa D-III Teknologi Informasi.
Gunakan HANYA data di bawah dan konsep dasar GA (kromosom biner, fitness, seleksi turnamen, crossover satu titik, mutasi, elitisme). Jangan mengarang data lain.

DATA
- Budget: Rp {h.budget} juta.{bobot}
- Jumlah part kandidat: {h.jumlah_kandidat}
- Parameter GA: populasi {h.ukuran_populasi}, generasi {h.generasi}, peluang mutasi {h.peluang_mutasi}
- Part terpilih: {terpilih}
- Total biaya Rp {h.total_biaya} juta, sisa budget Rp {h.sisa_budget} juta, total performa {h.total_nilai}
- {bf}
- Fitness terbaik per generasi: {riw}
- Fitness awal (generasi 1) {awal}, fitness akhir {akhir}, pertama kali mencapai nilai akhir di generasi {mulai_stabil}

TULIS 3 paragraf pendek (total maksimal 200 kata), bahasa Indonesia yang jelas, tanpa markdown, tanpa bullet, tanpa judul:
1) Arti kurva fitness: naik dari berapa ke berapa, kapan mulai stabil, dan kenapa kurvanya tidak pernah turun (elitisme).
2) Arti hasil: part yang dipilih, pemakaian budget, dan sisa budget.
3) Perbandingan dengan brute force (kalau ada) dan satu saran mengubah parameter GA."""


def _panggil(api_key, model, prompt, timeout=60):
    isi = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.4},
    }).encode("utf-8")
    req = urllib.request.Request(
        ALAMAT.format(model=model), data=isi, method="POST",
        headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    try:
        bagian = data["candidates"][0]["content"]["parts"]
        teks = "".join(b.get("text", "") for b in bagian).strip()
    except (KeyError, IndexError, TypeError):
        raise GeminiError(f"Gemini tidak mengembalikan jawaban ({str(data)[:200]})")
    if not teks:
        raise GeminiError("Gemini mengembalikan jawaban kosong.")
    return teks.replace("**", "").replace("##", "").replace("# ", "")


def jelaskan(api_key, model_utama, prompt):
    """Coba model utama, lalu model cadangan kalau model tidak ditemukan (404)."""
    urutan = [model_utama] + [m for m in MODEL_CADANGAN if m != model_utama]
    terakhir = ""
    for model in urutan:
        try:
            return _panggil(api_key, model, prompt)
        except urllib.error.HTTPError as e:
            isi = e.read().decode("utf-8", errors="replace")[:200]
            if e.code == 404:
                terakhir = f"model {model} tidak ditemukan"
                continue
            if e.code in (400, 401, 403):
                raise GeminiError(f"HTTP {e.code}: API key salah atau tidak punya izin. {isi}") from e
            if e.code == 429:
                raise GeminiError("Kuota Gemini habis atau terlalu sering. Tunggu 1 menit lalu coba lagi.") from e
            raise GeminiError(f"HTTP {e.code}: {isi}") from e
        except urllib.error.URLError as e:
            raise GeminiError(f"Gagal terhubung ke Gemini: {e.reason}") from e
    raise GeminiError(f"Semua model gagal ({terakhir}). Isi GEMINI_MODEL di .env dengan nama model yang valid.")
