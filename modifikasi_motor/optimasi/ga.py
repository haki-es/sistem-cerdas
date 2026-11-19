"""
Algoritma Genetika untuk optimasi modifikasi motor sport.

Logika ini dipindahkan dari notebook Praktikum 11 (Kegiatan 5, fungsi umum):
  - kromosom : list biner, 1 = part dipasang, 0 = tidak
  - fitness  : total poin performa, bernilai 0 jika ada batas (biaya/bobot) terlampaui
  - seleksi  : turnamen 2 kandidat
  - crossover: satu titik potong
  - mutasi   : tiap gen dibalik dengan peluang tertentu
  - elitisme : juara generasi langsung lolos
Modul ini murni Python (tanpa Django) supaya mudah diuji sendiri.
"""
import random
from itertools import product


def fitness_umum(krom, daftar, batas):
    """batas = dict, mis. {"biaya": 10.0} atau {"biaya": 12.0, "bobot": 6.0}."""
    total = {k: 0 for k in batas}              # penampung total per jenis batasan
    nilai = 0                                  # penampung total performa
    for i in range(len(daftar)):
        if krom[i] == 1:                       # part dipasang
            for k in batas:
                total[k] += daftar[i][k]       # tambah biaya / bobot
            nilai += daftar[i]["nilai"]        # tambah performa
    for k in batas:
        if round(total[k], 2) > batas[k]:      # salah satu batas terlampaui
            return 0                           # PENALTI: solusi gugur
    return nilai


def jalankan_ga(daftar, batas, ukuran=20, generasi=40, peluang_mutasi=0.1, seed=None):
    """Mengembalikan (kromosom_juara, riwayat_fitness_terbaik_per_generasi)."""
    rng = random.Random(seed)
    fit = lambda k: fitness_umum(k, daftar, batas)
    n = len(daftar)
    pop = [[rng.randint(0, 1) for _ in range(n)] for _ in range(ukuran)]   # populasi awal
    hist = []

    def pilih():                                                           # seleksi turnamen
        a, b = rng.sample(pop, 2)
        return a if fit(a) >= fit(b) else b

    for _ in range(generasi):
        anak = [max(pop, key=fit)]                                         # elitisme
        while len(anak) < ukuran:
            o1, o2 = pilih(), pilih()                                      # pilih dua orang tua
            t = rng.randint(1, n - 1)                                      # titik crossover
            calon = o1[:t] + o2[t:]                                        # crossover satu titik
            calon = [1 - g if rng.random() < peluang_mutasi else g for g in calon]  # mutasi
            anak.append(calon)
        pop = anak
        hist.append(fit(max(pop, key=fit)))                                # catat fitness terbaik
    return max(pop, key=fit), hist


def brute_force(daftar, batas):
    """Cek semua 2^n kombinasi untuk membuktikan apakah GA menemukan optimum."""
    terbaik = 0
    for kombinasi in product([0, 1], repeat=len(daftar)):
        terbaik = max(terbaik, fitness_umum(list(kombinasi), daftar, batas))
    return terbaik
