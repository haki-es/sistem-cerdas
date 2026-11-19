from decimal import Decimal

from django import forms

from .models import Part


class OptimasiForm(forms.Form):
    budget = forms.DecimalField(
        label="Budget modifikasi (juta Rp)", min_value=Decimal("0.1"),
        max_digits=6, decimal_places=2, initial=10,
    )
    batas_bobot = forms.DecimalField(
        label="Batas tambahan bobot (kg)", required=False, min_value=Decimal("0"),
        max_digits=5, decimal_places=2,
        help_text="Opsional. Kosongkan jika hanya dibatasi budget.",
    )
    part = forms.ModelMultipleChoiceField(
        label="Part kandidat", queryset=Part.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        help_text="Pilih minimal 2 part.",
    )
    ukuran = forms.IntegerField(label="Ukuran populasi", min_value=2, max_value=200, initial=20)
    generasi = forms.IntegerField(label="Jumlah generasi", min_value=1, max_value=300, initial=40)
    peluang_mutasi = forms.FloatField(
        label="Peluang mutasi (0-1)", min_value=0, max_value=1, initial=0.1,
        widget=forms.NumberInput(attrs={"step": "0.05"}),
    )
    bandingkan_bf = forms.BooleanField(
        label="Bandingkan dengan brute force", required=False, initial=True,
        help_text="Hanya dijalankan jika part kandidat 16 atau kurang.",
    )

    def clean_part(self):
        part = self.cleaned_data["part"]
        if part.count() < 2:
            raise forms.ValidationError("Pilih minimal 2 part.")
        return part
