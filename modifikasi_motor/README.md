# Optimasi Modifikasi Motor Sport (Django + Supabase)

Web untuk mencari kombinasi part modifikasi dengan total performa tertinggi di bawah batas budget,
memakai **algoritma genetika** dari Praktikum 11 (kromosom biner, seleksi turnamen, crossover satu titik,
mutasi, elitisme) dan pembuktian terhadap **brute force**. Hasil tiap optimasi disimpan di database (Supabase / PostgreSQL).

## Menjalankan di laptop (Windows)

```bash
cd modifikasi_motor
python -m venv venv
venv\Scripts\activate          # Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
```

1. Salin `.env.example` jadi `.env`.
2. Isi `DATABASE_URL` dengan connection string Supabase (Connect → **Session pooler**).
   Kalau dikosongkan, web otomatis pakai SQLite lokal (`db.sqlite3`) untuk uji coba.
3. Isi `SECRET_KEY` dengan string acak yang panjang.

```bash
python manage.py makemigrations optimasi
python manage.py migrate
python manage.py seed_part          # isi 10 part dari notebook P11
python manage.py createsuperuser    # untuk login /admin
python manage.py runserver
```

Buka http://127.0.0.1:8000

## Halaman

| URL | Fungsi |
|---|---|
| `/` | Form optimasi (budget, batas bobot opsional, pilih part, parameter GA) + daftar part |
| `/hasil/<id>/` | Part terpilih, total biaya/performa, GA vs brute force, kurva fitness |
| `/riwayat/` | 50 optimasi terakhir |
| `/admin/` | Kelola part (tambah/ubah biaya dan performa) dan lihat riwayat |

## API key Supabase (opsional)

Koneksi utama Django memakai `DATABASE_URL`. API key dipakai untuk Data API Supabase, dicoba lewat halaman `/cek-supabase/` (khusus staff, login lewat `/admin/`).

1. Di dashboard Supabase buka **Settings > API Keys**, ambil Project URL, publishable key (`sb_publishable_...`) dan secret key (`sb_secret_...`).
2. Isi `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY`, `SUPABASE_SECRET_KEY` di `.env`, lalu restart server.
3. Login `/admin/`, buka `/cek-supabase/`.

Secret key hanya boleh dipakai di server. Jangan taruh di template, JavaScript, atau Git.

## Penjelasan AI (Gemini)

Di halaman hasil, tombol **Jelaskan dengan AI** meminta Gemini menjelaskan kurva fitness dan hasil optimasi. Penjelasannya disimpan di database.
1. Buat API key gratis di Google AI Studio, isi `GEMINI_API_KEY` di `.env` (opsional `GEMINI_MODEL`).
2. `python manage.py migrate` lalu restart server.

## Struktur

- `optimasi/ga.py` — logika GA (fungsi umum dari Kegiatan 5 notebook P11), murni Python.
- `optimasi/models.py` — `Part` dan `HasilOptimasi`.
- `optimasi/management/commands/seed_part.py` — data awal: 8 part Pengembangan 1, plus Quickshifter dan Radiator racing dari Latihan 2 (nonaktif secara default).

## Catatan Supabase

Tabel yang dibuat Django berada di schema `public`, dan Supabase membuka schema itu lewat Data API.
Supaya tabel tidak bisa diakses lewat API publik, aktifkan Row Level Security di **SQL Editor** setelah `migrate`:

```sql
do $$
declare r record;
begin
  for r in select tablename from pg_tables where schemaname = 'public' loop
    execute format('alter table public.%I enable row level security', r.tablename);
  end loop;
end $$;
```

Django tetap bisa mengakses tabel karena terhubung langsung sebagai user database. Jalankan ulang web setelah ini untuk memastikan semuanya normal.
