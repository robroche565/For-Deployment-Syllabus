from django.db import models
from django.conf import settings
from django.utils import timezone
import os

# Create your models here.

# ----- Syllabus Template -----
class Syllabus_Template(models.Model):
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=255, null=True)
    sem = models.CharField(max_length=10, choices=[('1st', '1st'), ('2nd', '2nd'), ('SUMMER', 'SUMMER')], blank=True, null=True)
    school_year = models.CharField(max_length=9, blank=True, null=True)
    revision_status = models.CharField(max_length=50, default='1st Draft')
    revision_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    
    # Override functions
    # check if 'revision_date' field is not already set (i.e., it's None), and if so, we set it to the current date and time using timezone.now().
    def save(self, *args, **kwargs):
        if not self.revision_date:
            self.revision_date = timezone.now()

        if not self.created_at:
            self.created_at = timezone.now()

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        logos_to_delete = Logo.objects.filter(syllabus_template_id=self.id)

        for logo in logos_to_delete:
            image_path = os.path.join(settings.MEDIA_ROOT, logo.img_name)

            if os.path.exists(image_path):
                os.remove(image_path)
            logo.delete()

        # Call the parent class's delete method to delete the Syllabus_Template instance
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.name

# ----- Syllabus Template Content -----
class Logo(models.Model):
    syllabus_template_id = models.ForeignKey(Syllabus_Template, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=100, null=False)
    img_name = models.CharField(max_length=250, null=False)
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    
class Vision(models.Model):
    syllabus_template_id = models.ForeignKey(Syllabus_Template, on_delete=models.CASCADE, blank=True, null=True)
    vision = models.TextField()
    default = models.BooleanField(default=False)

class Vision_Itemize(models.Model):
    syllabus_template_id = models.ForeignKey(Syllabus_Template, on_delete=models.CASCADE, blank=True, null=True)
    vision_itemize = models.TextField()

class Mission(models.Model):
    syllabus_template_id = models.ForeignKey(Syllabus_Template, on_delete=models.CASCADE, blank=True, null=True)
    mission = models.TextField()
    default = models.BooleanField(default=False)
    
class Mission_Itemize(models.Model):
    syllabus_template_id = models.ForeignKey(Syllabus_Template, on_delete=models.CASCADE, blank=True, null=True)
    mission_itemize = models.TextField()
    default = models.BooleanField(default=False)

class Goal(models.Model):
    syllabus_template_id = models.ForeignKey(Syllabus_Template, on_delete=models.CASCADE, null=True)
    goal = models.TextField()

class Goal_Itemize(models.Model):
    syllabus_template_id = models.ForeignKey(Syllabus_Template, on_delete=models.CASCADE, null=True)
    goal_itemize = models.TextField()

class Course_Outcome(models.Model):
    syllabus_template_id = models.ForeignKey(Syllabus_Template, on_delete=models.CASCADE, null=True)
    course_outcome = models.TextField()

# ----- Grading System -----
class Grading_System(models.Model):
    syllabus_template_id = models.ForeignKey(Syllabus_Template, on_delete=models.CASCADE, null=True)
    grading_system_type = models.CharField(max_length=25, blank=True, null=True)
    # passing_grade = models.SmallIntegerField(null=True)
    # sample_computation = models.CharField(max_length=100, null=True)

class Term_Grade(models.Model):
    grading_system_id = models.ForeignKey(Grading_System, on_delete=models.CASCADE, null=True)
    term_name = models.CharField(max_length=50)
    term_percentage = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.term_name

class Term_Description(models.Model):
    term_grade_id = models.ForeignKey(Term_Grade, on_delete=models.CASCADE, null=True)
    term_description = models.CharField(max_length=255)
    percentage = models.SmallIntegerField(blank=True, null=True)
    lecture_percentage = models.SmallIntegerField(blank=True, null=True)
    laboratory_percentage = models.SmallIntegerField(blank=True, null=True)

class Percentage_Grade_Range(models.Model):
    grading_system_id = models.ForeignKey(Grading_System, on_delete=models.CASCADE, blank=True, null=True)
    min_range = models.SmallIntegerField(blank=True, null=True)
    max_range = models.SmallIntegerField(blank=True, null=True)
    grade = models.FloatField(blank=True, null=True)
    default = models.BooleanField(default=False)