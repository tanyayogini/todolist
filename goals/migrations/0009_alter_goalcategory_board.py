# Generated by Django 4.0.1 on 2023-07-20 06:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('goals', '0008_create_new_objects'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goalcategory',
            name='board',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='categories', to='goals.board', verbose_name='Доска'),
        ),
    ]
