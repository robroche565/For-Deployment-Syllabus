# Generated by Django 4.2.4 on 2023-11-25 15:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='verified',
            field=models.CharField(blank=True, choices=[('Yes', 'Yes'), ('No', 'No')], default='No', max_length=3, null=True),
        ),
    ]