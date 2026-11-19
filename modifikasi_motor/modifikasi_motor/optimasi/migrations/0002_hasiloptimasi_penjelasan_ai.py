from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("optimasi", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="hasiloptimasi",
            name="penjelasan_ai",
            field=models.TextField(blank=True, default=""),
        ),
    ]
