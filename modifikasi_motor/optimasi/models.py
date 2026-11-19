from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Part(models.Model):
    """Part modifikasi motor yang menjadi kandidat (gen pada kromosom)."""

    nama = models.CharField(max_length=100, unique=True)
    biaya = models.DecimalField(
        max_digits=6, decimal_places=2, help_text="Biaya part dalam juta rupiah"
    )
    bobot = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        help_text="Tambahan bobot (kg), opsional. Dipakai kalau ada batas bobot",
    )
    nilai = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Poin performa (skala 1-10)",
    )
    aktif = models.BooleanField(default=True, help_text="Dicentang otomatis di form optimasi")

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.nama} (Rp {self.biaya} jt, performa {self.nilai})"


class HasilOptimasi(models.Model):
    """Riwayat satu kali jalannya algoritma genetika."""

    dibuat = models.DateTimeField(auto_now_add=True)
    budget = models.FloatField()
    batas_bobot = models.FloatField(null=True, blank=True)
    ukuran_populasi = models.PositiveIntegerField()
    generasi = models.PositiveIntegerField()
    peluang_mutasi = models.FloatField()
    jumlah_kandidat = models.PositiveIntegerField()
    part_terpilih = models.JSONField(default=list)      # snapshot part yang dipasang
    total_biaya = models.FloatField(default=0)
    total_bobot = models.FloatField(default=0)
    total_nilai = models.PositiveIntegerField(default=0)
    optimum_bf = models.PositiveIntegerField(null=True, blank=True)   # optimum brute force
    cocok_bf = models.BooleanField(null=True, blank=True)             # GA == brute force?
    riwayat_fitness = models.JSONField(default=list)    # fitness terbaik per generasi
    penjelasan_ai = models.TextField(blank=True, default="")   # penjelasan dari Gemini

    class Meta:
        ordering = ["-dibuat"]
        verbose_name_plural = "hasil optimasi"

    def __str__(self):
        return f"Optimasi {self.dibuat:%d/%m/%Y %H:%M} - budget Rp {self.budget} jt"

    @property
    def sisa_budget(self):
        return round(self.budget - self.total_biaya, 2)
