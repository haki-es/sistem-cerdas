import json

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from . import gemini, supabase_api
from .forms import OptimasiForm
from .ga import brute_force, fitness_umum, jalankan_ga
from .models import HasilOptimasi, Part

MAKS_PART_BRUTE_FORCE = 16   # 2^16 = 65.536 kombinasi masih cepat


def _proses(data):
    """Jalankan GA dari data form, simpan hasilnya ke database."""
    daftar = [
        {"nama": p.nama, "biaya": float(p.biaya), "bobot": float(p.bobot), "nilai": p.nilai}
        for p in data["part"]
    ]
    batas = {"biaya": float(data["budget"])}
    if data.get("batas_bobot") is not None:
        batas["bobot"] = float(data["batas_bobot"])

    juara, riwayat = jalankan_ga(
        daftar, batas,
        ukuran=data["ukuran"], generasi=data["generasi"],
        peluang_mutasi=data["peluang_mutasi"],
    )
    fit = fitness_umum(juara, daftar, batas)
    # fitness 0 berarti tidak ada paket yang muat/menguntungkan -> tidak ada part dipasang
    terpilih = [daftar[i] for i in range(len(daftar)) if juara[i] == 1] if fit > 0 else []

    optimum, cocok = None, None
    if data.get("bandingkan_bf") and len(daftar) <= MAKS_PART_BRUTE_FORCE:
        optimum = brute_force(daftar, batas)
        cocok = (fit == optimum)

    return HasilOptimasi.objects.create(
        budget=batas["biaya"],
        batas_bobot=batas.get("bobot"),
        ukuran_populasi=data["ukuran"],
        generasi=data["generasi"],
        peluang_mutasi=data["peluang_mutasi"],
        jumlah_kandidat=len(daftar),
        part_terpilih=terpilih,
        total_biaya=round(sum(p["biaya"] for p in terpilih), 2),
        total_bobot=round(sum(p["bobot"] for p in terpilih), 2),
        total_nilai=fit,
        optimum_bf=optimum,
        cocok_bf=cocok,
        riwayat_fitness=riwayat,
    )


def index(request):
    if request.method == "POST":
        form = OptimasiForm(request.POST)
        if form.is_valid():
            hasil = _proses(form.cleaned_data)
            return redirect("hasil", pk=hasil.pk)
    else:
        form = OptimasiForm(initial={"part": Part.objects.filter(aktif=True)})
    return render(request, "optimasi/index.html", {"form": form, "daftar_part": Part.objects.all()})


def hasil(request, pk):
    return render(request, "optimasi/hasil.html", {"hasil": get_object_or_404(HasilOptimasi, pk=pk)})


def riwayat(request):
    return render(request, "optimasi/riwayat.html", {"daftar": HasilOptimasi.objects.all()[:50]})


@staff_member_required
def cek_supabase(request):
    """Uji koneksi Supabase Data API memakai publishable key dan secret key (khusus staff)."""
    hasil_cek = []
    for label, key in (
        ("Publishable key (publik)", settings.SUPABASE_PUBLISHABLE_KEY),
        ("Secret key (server)", settings.SUPABASE_SECRET_KEY),
    ):
        item = {"label": label, "diisi": bool(key), "ok": False, "jumlah": 0, "json": "", "galat": ""}
        if key and settings.SUPABASE_URL:
            try:
                data = supabase_api.ambil_tabel(settings.SUPABASE_URL, key, "optimasi_part", batas=5)
                item.update(ok=True, jumlah=len(data), json=json.dumps(data, indent=2, ensure_ascii=False))
            except supabase_api.SupabaseAPIError as e:
                item["galat"] = str(e)
        hasil_cek.append(item)
    return render(request, "optimasi/cek_supabase.html", {
        "url_diisi": bool(settings.SUPABASE_URL),
        "url": settings.SUPABASE_URL,
        "hasil_cek": hasil_cek,
    })


@require_POST
def penjelasan_ai(request, pk):
    """Minta Gemini menjelaskan hasil optimasi, lalu simpan di database."""
    h = get_object_or_404(HasilOptimasi, pk=pk)
    if not settings.GEMINI_API_KEY:
        messages.error(request, "GEMINI_API_KEY belum diisi di file .env.")
    else:
        try:
            h.penjelasan_ai = gemini.jelaskan(settings.GEMINI_API_KEY, settings.GEMINI_MODEL, gemini.buat_prompt(h))
            h.save(update_fields=["penjelasan_ai"])
        except gemini.GeminiError as e:
            messages.error(request, f"Gagal membuat penjelasan AI: {e}")
    return redirect(reverse("hasil", args=[pk]) + "#penjelasan")
