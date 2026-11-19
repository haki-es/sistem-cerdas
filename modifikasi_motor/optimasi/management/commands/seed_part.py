from decimal import Decimal

from django.core.management.base import BaseCommand

from optimasi.models import Part

# (nama, biaya juta Rp, poin performa, aktif)
# 8 part pertama = Pengembangan 1 (P11). 2 part terakhir = tambahan Latihan 2 (nonaktif secara default).
DATA_PART = [
    ("Knalpot racing slip-on", "3.5", 9, True),
    ("ECU remap", "2.5", 8, True),
    ("Shock belakang upgrade", "3.0", 7, True),
    ("Ban sport", "2.0", 6, True),
    ("Kampas rem racing", "1.2", 5, True),
    ("Filter udara racing", "0.8", 4, True),
    ("Footstep racing", "1.5", 3, True),
    ("Lampu LED", "0.7", 2, True),
    ("Quickshifter", "2.8", 7, False),
    ("Radiator racing", "1.6", 4, False),
]


class Command(BaseCommand):
    help = "Isi tabel Part dengan data modifikasi motor sport dari notebook P11."

    def handle(self, *args, **options):
        dibuat = 0
        for nama, biaya, nilai, aktif in DATA_PART:
            _, baru = Part.objects.get_or_create(
                nama=nama, defaults={"biaya": Decimal(biaya), "nilai": nilai, "aktif": aktif}
            )
            dibuat += int(baru)
        self.stdout.write(self.style.SUCCESS(f"Selesai. {dibuat} part baru ditambahkan."))
