# Generated by Django 5.2 on 2025-06-30 13:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('EldenRingInsider', '0012_rename_effect_item_effects'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='spell_requirements',
        ),
        migrations.AddField(
            model_name='item',
            name='fp_cost',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
