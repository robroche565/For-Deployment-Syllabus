from django.db import models
from django.conf import settings
from syllabus_template.models import Syllabus_Template

# Create your models here.
class Syllabus_AI(models.Model):
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    raw_source = models.TextField(null=True, blank=True)
    raw_topics = models.TextField(null=True, blank=True)
    raw_course_outline = models.TextField(null=False, blank=True)
    raw_course_learning_outcomes = models.TextField(null=True, blank=True)
    raw_course_learning_outcomes_ai_with_letters = models.TextField(null=True, blank=True)
 
    raw_first_prompt = models.TextField(null=True, blank=True)
    raw_first_response = models.TextField(null=True, blank=True)
    raw_second_prompt = models.TextField(null=True, blank=True)
    raw_second_response = models.TextField(null=True, blank=True)
    
    YES, NO = 'Yes', 'No'
    FIRST_TIME_PROCESSING_CHOICES = [(YES, 'Yes'), (NO, 'No')]
    first_time_processing = models.CharField(
        max_length=3,
        choices=FIRST_TIME_PROCESSING_CHOICES,
        null=True, blank=True, default=YES
    )
    ENGLISH, FILIPINO = 'English', 'Filipino'
    LANGUAGE_CHOICES = [(ENGLISH, 'English'), (FILIPINO, 'Filipino')]

    language = models.CharField(
        max_length=10,
        choices=LANGUAGE_CHOICES,
        default=ENGLISH
    )


# ----- Sources -----
class Sources(models.Model):
    syllabus_ai_id = models.ForeignKey(Syllabus_AI, on_delete=models.CASCADE, null=True)
    reference = models.TextField()
    
# ----- Topic -----
class Topic(models.Model):
    syllabus_ai_id = models.ForeignKey(Syllabus_AI, on_delete=models.CASCADE, null=True)
    topic_name = models.TextField()

# ---------- COURSE LEARNING OUTCOMES ----------
class Course_Learning_Outcome(models.Model):
    syllabus_ai_id = models.ForeignKey(Syllabus_AI, on_delete=models.CASCADE, null=True)
    course_learning_outcome = models.TextField(blank=True, null=True)


# ---------- COURSE OUTLINE ----------
class Course_Outline(models.Model):
    syllabus_ai_id = models.ForeignKey(Syllabus_AI, on_delete=models.CASCADE, null=True)
    week = models.CharField(max_length=100, blank=True, null=True)
    topic = models.TextField(blank=True, null=True)
    course_learning_outcomes = models.CharField(max_length=50, blank=True, null=True)

class Course_Content(models.Model):
    course_outline_id = models.ForeignKey(Course_Outline, on_delete=models.CASCADE)
    course_content = models.TextField()

class Desired_Student_Learning_Outcome(models.Model):
    course_outline_id = models.ForeignKey(Course_Outline, on_delete=models.CASCADE)
    dslo = models.TextField()

class Outcome_Based_Activity(models.Model):
    course_outline_id = models.ForeignKey(Course_Outline, on_delete=models.CASCADE)
    oba = models.TextField()

class Evidence_of_Outcome(models.Model):
    course_outline_id = models.ForeignKey(Course_Outline, on_delete=models.CASCADE)
    eoo = models.TextField()
    
class Values_Intended(models.Model):
    course_outline_id = models.ForeignKey(Course_Outline, on_delete=models.CASCADE)
    values = models.TextField()


# ---------- COURSE RUBRIC ----------
class Course_Rubric(models.Model):
    syllabus_ai_id = models.ForeignKey(Syllabus_AI, on_delete=models.CASCADE, null=True)
    raw_source_course_rubric_ai = models.TextField(null=False, blank=True)
    title = models.CharField(max_length=150, blank=True, null=True)

    def __str__(self):
        return self.title

class Course_Rubric_Item(models.Model):
    course_rubric_id = models.ForeignKey(Course_Rubric, on_delete=models.CASCADE, null=True)
    criteria = models.CharField(max_length=150, blank=True, null=True)
    beginner = models.CharField(max_length=150, blank=True, null=True)
    capable = models.CharField(max_length=150, blank=True, null=True)
    accomplished = models.CharField(max_length=150, blank=True, null=True)
    expert = models.CharField(max_length=150, blank=True, null=True)

