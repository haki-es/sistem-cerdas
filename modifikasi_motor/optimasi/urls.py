from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("hasil/<int:pk>/", views.hasil, name="hasil"),
    path("riwayat/", views.riwayat, name="riwayat"),
    path("hasil/<int:pk>/penjelasan/", views.penjelasan_ai, name="penjelasan_ai"),
    path("cek-supabase/", views.cek_supabase, name="cek_supabase"),
]
