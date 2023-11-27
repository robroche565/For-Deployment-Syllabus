# Generated by Django 4.2.7 on 2023-11-23 03:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('syllabus_template', '0001_initial'),
        ('syllabus_ai', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Syllabus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('syllabus_name', models.CharField(blank=True, max_length=255, null=True)),
                ('time_frame', models.IntegerField(blank=True, null=True)),
                ('college', models.CharField(blank=True, max_length=255, null=True)),
                ('department', models.CharField(blank=True, max_length=255, null=True)),
                ('course_code', models.CharField(blank=True, max_length=255, null=True)),
                ('course_name', models.CharField(blank=True, max_length=255, null=True)),
                ('course_credit', models.FloatField(blank=True, null=True)),
                ('course_credit_description', models.TextField(blank=True, null=True)),
                ('course_description', models.TextField(blank=True, null=True)),
                ('grading_system_option', models.CharField(blank=True, max_length=50, null=True)),
                ('source_type', models.CharField(blank=True, max_length=50, null=True)),
                ('semester', models.CharField(blank=True, max_length=50, null=True)),
                ('school_year', models.CharField(blank=True, max_length=255, null=True)),
                ('recommending_approval_name', models.CharField(blank=True, max_length=255, null=True)),
                ('recommending_approval_position', models.CharField(blank=True, max_length=255, null=True)),
                ('concured_name', models.CharField(blank=True, max_length=255, null=True)),
                ('concured_position', models.CharField(blank=True, max_length=255, null=True)),
                ('approved_name', models.CharField(blank=True, max_length=255, null=True)),
                ('approved_position', models.CharField(blank=True, max_length=255, null=True)),
                ('footer_info', models.CharField(blank=True, max_length=255, null=True)),
                ('revision_status', models.SmallIntegerField(default=1)),
                ('revision_date', models.DateTimeField(blank=True, null=True)),
                ('effective_date', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(blank=True, null=True)),
                ('syllabus_ai_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='syllabus_ai.syllabus_ai')),
                ('syllabus_template_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='syllabus_template.syllabus_template')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Syllabus_Grading_System',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grading_system_type', models.CharField(blank=True, max_length=25, null=True)),
                ('syllabus_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='syllabus.syllabus')),
            ],
        ),
        migrations.CreateModel(
            name='Syllabus_Term_Grade',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('term_name', models.CharField(max_length=50)),
                ('term_percentage', models.IntegerField(blank=True, null=True)),
                ('grading_system_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='syllabus.syllabus_grading_system')),
            ],
        ),
        migrations.CreateModel(
            name='Syllabus_Term_Description',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('term_description', models.CharField(max_length=255)),
                ('percentage', models.SmallIntegerField(blank=True, null=True)),
                ('lecture_percentage', models.SmallIntegerField(blank=True, null=True)),
                ('laboratory_percentage', models.SmallIntegerField(blank=True, null=True)),
                ('term_grade_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='syllabus.syllabus_term_grade')),
            ],
        ),
        migrations.CreateModel(
            name='Syllabus_Percentage_Grade_Range',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('min_range', models.SmallIntegerField(blank=True, null=True)),
                ('max_range', models.SmallIntegerField(blank=True, null=True)),
                ('grade', models.FloatField(blank=True, null=True)),
                ('default', models.BooleanField(default=False)),
                ('grading_system_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='syllabus.syllabus_grading_system')),
            ],
        ),
        migrations.CreateModel(
            name='Preriquisite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('preriquisite', models.CharField(max_length=255)),
                ('syllabus_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='syllabus.syllabus')),
            ],
        ),
        migrations.CreateModel(
            name='Prepared',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fullname', models.CharField(max_length=255)),
                ('syllabus_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='syllabus.syllabus')),
            ],
        ),
        migrations.CreateModel(
            name='Course_Requirements',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('requirements', models.CharField(max_length=255)),
                ('syllabus_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='syllabus.syllabus')),
            ],
        ),
    ]
