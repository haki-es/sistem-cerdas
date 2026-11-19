from django.contrib import admin

from .models import HasilOptimasi, Part


@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    list_display = ("nama", "biaya", "bobot", "nilai", "aktif")
    list_editable = ("biaya", "bobot", "nilai", "aktif")
    search_fields = ("nama",)


@admin.register(HasilOptimasi)
class HasilOptimasiAdmin(admin.ModelAdmin):
    list_display = ("dibuat", "budget", "total_biaya", "total_nilai", "optimum_bf", "cocok_bf")
    readonly_fields = [f.name for f in HasilOptimasi._meta.fields]
