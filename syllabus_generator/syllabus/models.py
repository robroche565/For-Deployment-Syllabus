from syllabus_template.models import Syllabus_Template
from syllabus_ai.models import Syllabus_AI
from django.db import models
from django.conf import settings
from django.utils import timezone
import os

# Create your models here.
class Syllabus(models.Model):
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    syllabus_template_id = models.ForeignKey(Syllabus_Template, on_delete=models.SET_NULL, null=True)
    syllabus_ai_id = models.ForeignKey(Syllabus_AI, on_delete=models.CASCADE, null=True)
    syllabus_name = models.CharField(max_length=255, blank=True, null=True)
    time_frame = models.IntegerField(blank=True, null=True)
    college = models.CharField(max_length=255, blank=True, null=True)
    bachelor = models.CharField(max_length=255, blank=True, null=True)
    department = models.CharField(max_length=255, blank=True, null=True)
    course_code = models.CharField(max_length=255, blank=True, null=True)
    course_name = models.CharField(max_length=255, blank=True, null=True)
    course_credit = models.FloatField(blank=True, null=True)
    course_credit_description = models.TextField(blank=True, null=True)
    course_description = models.TextField(blank=True, null=True)
    grading_system_option = models.CharField(max_length=50, blank=True, null=True)
    source_type = models.CharField(max_length=50, blank=True, null=True)
    semester = models.CharField(max_length=50, blank=True, null=True)
    school_year = models.CharField(max_length=255, blank=True, null=True)
    recommending_approval_name = models.CharField(max_length=255, blank=True, null=True)
    recommending_approval_position = models.CharField(max_length=255, blank=True, null=True)
    concured_name = models.CharField(max_length=255, blank=True, null=True)
    concured_position = models.CharField(max_length=255, blank=True, null=True)
    approved_name = models.CharField(max_length=255, blank=True, null=True)
    approved_position = models.CharField(max_length=255, blank=True, null=True)
    footer_info = models.CharField(max_length=255, blank=True, null=True)

    revision_status = models.SmallIntegerField(default=1)
    revision_date = models.DateTimeField(blank=True, null=True)
    effective_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    # Override functions
    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = timezone.now()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.syllabus_name

# ---------- Syllabus Content ----------
class Preriquisite(models.Model):
    syllabus_id = models.ForeignKey(Syllabus, on_delete=models.CASCADE)
    preriquisite = models.CharField(max_length=255)

# ----- Grading System -----
class Syllabus_Grading_System(models.Model):
    syllabus_id = models.ForeignKey(Syllabus, on_delete=models.CASCADE, null=True)
    grading_system_type = models.CharField(max_length=25, blank=True, null=True)

class Syllabus_Term_Grade(models.Model):
    grading_system_id = models.ForeignKey(Syllabus_Grading_System, on_delete=models.CASCADE, null=True)
    term_name = models.CharField(max_length=50)
    term_percentage = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.term_name

class Syllabus_Term_Description(models.Model):
    term_grade_id = models.ForeignKey(Syllabus_Term_Grade, on_delete=models.CASCADE, null=True)
    term_description = models.CharField(max_length=255)
    percentage = models.SmallIntegerField(blank=True, null=True)
    lecture_percentage = models.SmallIntegerField(blank=True, null=True)
    laboratory_percentage = models.SmallIntegerField(blank=True, null=True)

class Syllabus_Percentage_Grade_Range(models.Model):
    grading_system_id = models.ForeignKey(Syllabus_Grading_System, on_delete=models.CASCADE, blank=True, null=True)
    min_range = models.SmallIntegerField(blank=True, null=True)
    max_range = models.SmallIntegerField(blank=True, null=True)
    grade = models.FloatField(blank=True, null=True)
    default = models.BooleanField(default=False)

# ----- Course Requirements -----
class Course_Requirements(models.Model):
    syllabus_id = models.ForeignKey(Syllabus, on_delete=models.CASCADE, null=True)
    requirements = models.CharField(max_length=255)

# ----- Prepared by -----
class Prepared(models.Model):
    syllabus_id = models.ForeignKey(Syllabus, on_delete=models.CASCADE, null=True)
    fullname = models.CharField(max_length=255)

    def __str__(self):
        return self.fullname