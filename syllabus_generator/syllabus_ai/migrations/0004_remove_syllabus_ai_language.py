# Generated by Django 4.2.4 on 2023-11-27 05:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('syllabus_ai', '0003_syllabus_ai_language'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='syllabus_ai',
            name='language',
        ),
    ]
