from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.views.generic import TemplateView, View, DeleteView
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import IntegrityError
from django.contrib.auth import get_user_model, update_session_auth_hash
from datetime import datetime
from django.utils import timezone
from django.conf import settings
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.urls import reverse
from django.db import transaction
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.hashers import make_password
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site

import json
import ast
from django.http import Http404

# models/database, form
import os
from .forms import *
from syllabus_template.models import *
from syllabus.models import *
from django.db.models import Count
import time

#import
import re
import openai
import datetime
import requests

#models
from django.contrib.auth.models import User
from account.models import Account, CustomUser
from syllabus_ai.models import *

# pdf libraries import
from weasyprint import CSS, HTML
from django.template import loader

# Get an instance of a logger
User = get_user_model()
custom_username_validator = UnicodeUsernameValidator()


# Initialize an empty conversation history
conversation_history = []


def reset_conversation():
    global conversation_history
    conversation_history = []


def ask_openai(message):
    openai.api_key = settings.OPENAI_API_KEY

    # Append the user's message to the conversation history
    conversation_history.append({"role": "user", "content": message})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k", messages=conversation_history, max_tokens=15000)

    # Get the assistant's reply from the response
    try:
        answer = response['choices'][0]['message']['content'].replace('<br>', '').replace('\n', '')
    except:
        answer = 'Oops try again'

    # Append the assistant's reply to the conversation history
    conversation_history.append({"role": "assistant", "content": answer})

    reset_conversation()
    return answer

#if you want to have separate keys just add in the settings
def ask_openaiextra(message):
    openai.api_key = settings.OPENAI_API_KEY_EXTRA

    # Append the user's message to the conversation history
    conversation_history.append({"role": "user", "content": message})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k", messages=conversation_history, max_tokens=15000)

    # Get the assistant's reply from the response
    try:
        answer = response['choices'][0]['message']['content'].replace('<br>', '').replace('\n', '')
    except:
        answer = 'Oops try again'

    # Append the assistant's reply to the conversation history
    conversation_history.append({"role": "assistant", "content": answer})

    reset_conversation()
    return answer


def landing_view (request):
    return render(request, 'landing.html')

CustomUser = get_user_model()

def forgot_pass_view(request):
    return render(request, 'password/send_email_forgot.html')

def forgot_pass_confirm_sent_view(request):
    # Retrieve the email from the query parameters
    email = request.GET.get('email')

    # Pass the email as context to the template
    context = {'email': email}

    return render(request, 'password/send_email_confirm.html', context)

User = get_user_model()

@method_decorator(csrf_exempt, name='dispatch')
class ForgotPasswordSubmitView(View):
    def post(self, request, *args, **kwargs):
        email = request.POST.get('email')

        # Check if the email exists in your user database
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'No account found with that email address.'})

        # Generate a unique token for password reset using Django's default_token_generator
        token = default_token_generator.make_token(user)

        # Build the password reset URL
        reset_url = request.build_absolute_uri(reverse('change_password', kwargs={'uidb64': urlsafe_base64_encode(force_bytes(user.pk)), 'token': token}))

        # Send email
        subject = 'Reset Your Password'
        message = f'Click the following link to reset your password: {reset_url}'
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [user.email]
        send_mail(subject, message, from_email, to_email)

        # Redirect to the 'forgot_password_sent' URL
        redirect_url = redirect('forgot_password_sent')
        redirect_url['Location'] += f'?email={email}'
        return redirect_url

def change_password_view(request, uidb64, token):
    try:
        user_id = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=user_id)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return HttpResponseBadRequest('Invalid user ID')

    if not default_token_generator.check_token(user, token):
        return HttpResponseBadRequest('Invalid token')

    return render(request, 'password/password_change.html', {'uidb64': uidb64, 'token': token})

def process_change_password(request, uidb64, token):
    try:
        user_id = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=user_id)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return HttpResponseBadRequest('Invalid user ID')

    if not default_token_generator.check_token(user, token):
        return HttpResponseBadRequest('Invalid token')

    if request.method == 'POST':
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')

        if new_password1 and new_password1 == new_password2:
            # Update user's password
            user.password = make_password(new_password1)
            user.save()

            # Update session authentication hash
            update_session_auth_hash(request, user)

            messages.success(request, 'Your password was successfully updated!')
            return redirect('success_reset_password')  # Change the URL name to match your URL configuration
        else:
            messages.error(request, 'Passwords do not match.')

    return render(request, 'password/password_change.html', {'uidb64': uidb64, 'token': token})

def success_reset_view (request):
    return render(request, 'password/password_change_success.html')



def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        if email.endswith('@wmsu.edu.ph'):
            user = auth.authenticate(request, username=email, password=password)

            if user is not None:
                if user.account.verified == 'Yes':
                    auth.login(request, user)
                    return redirect('userpage')
                else:
                    verification_link = reverse('send_verification')
                    error_message = mark_safe(f'User is not yet verified. Please check your Email for the Verification. <a href="{verification_link}">Resend Confirmation</a>')
            else:
                error_message = 'Invalid email or password'
        else:
            error_message = 'You must use your WMSU E-mail'

        return render(request, 'login/login.html', {'error_message': error_message})

    return render(request, 'login/login.html')

def send_verif_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        # Check if the email exists in your user model
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            # Handle the case where the email doesn't exist
            # You may want to redirect the user or show an error message
            pass
        else:
            # Generate a verification token
            token = default_token_generator.make_token(user)

            # Build the verification URL
            current_site = get_current_site(request)
            verification_url = reverse('verify_email', args=[urlsafe_base64_encode(force_bytes(user.pk)), token])
            verification_url = f'http://{current_site.domain}{verification_url}'

            # Send the verification email
            subject = 'Verify your email address'
            message = f'Click the following link to verify your Account: {verification_url}'
            from_email = settings.DEFAULT_FROM_EMAIL  # Set your email here
            to_email = [user.email]
            send_mail(subject, message, from_email, to_email, fail_silently=False)

            # Update the Account model or set a flag indicating that the verification email has been sent

            # Redirect to the success page with email parameter
            redirect_url = redirect('sent_verification')
            if email:
                redirect_url['Location'] += f'?email={email}'
            return redirect_url
            #return redirect('sent_verification')

    return render(request, 'verification/send_verification.html')

def verify_email(request, uidb64, token):
    UserModel = get_user_model()
    try:
        # Decode the user ID from base64
        uid = force_str(urlsafe_base64_decode(uidb64))
        # Get the user with the decoded ID
        user = UserModel.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
        user = None

    # Initialize the email variable to an empty string
    email = ""

    # Check if the user exists and if the token is valid
    if user is not None and default_token_generator.check_token(user, token):
        # Update the account verification status
        user.account.verified = 'Yes'
        user.account.save()

        # Retrieve the email for display in the template
        email = user.email

    # Pass the email to the template context
    return render(request, 'verification/email_confirm_success.html', {'email': email})

def sent_verif_success_view (request):
    # Retrieve the email from the query parameters
    email = request.GET.get('email')

    # Pass the email as context to the template
    context = {'email': email}

    return render(request, 'verification/send_verification_success.html', context)

    #return render(request, 'verification/send_verification_success.html')

def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        first_name = request.POST['first_name'].strip().capitalize()   # Remove leading and trailing spaces
        middle_name = request.POST['middle_name'].strip().capitalize()   # Remove leading and trailing spaces
        last_name = request.POST['last_name'].strip().capitalize()   # Remove leading and trailing spaces
        wmsu_email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        # Initialize an empty dictionary to store error messages
        error_messages = {}

        # Check if the username is already taken
        if CustomUser.objects.filter(username=username).exists():
            error_messages['username'] = "Username is already taken"

        # Check if first name, middle name, and last name contain consecutive spaces
        if re.search(r'\s{2,}', first_name) or re.search(r'\s{2,}', middle_name) or re.search(r'\s{2,}', last_name):
            error_messages['name_format'] = "First name, Middle name, and Last name cannot contain consecutive spaces."

        # Check if the email ends with '@wmsu.edu.ph'
        if not wmsu_email.endswith('@wmsu.edu.ph'):
            error_messages['email_ends'] = "You must use your WMSU E-mail"

        # Check if the WMSU email is already taken
        if CustomUser.objects.filter(email=wmsu_email).exists():
            error_messages['email_checker'] = "WMSU email is already taken"


        # If there are any error messages, return them to the template
        if error_messages:
            return render(request, 'login/signup.html', {'error_messages': error_messages})

        try:
            # Create the user with provided data using the CustomUser manager
            user = CustomUser.objects.create_user(username=username, email=wmsu_email, password=password1)
            # Create the Account instance and link it to the user
            account = Account.objects.create(
                user=user,
                first_name=first_name,
                middle_name=middle_name,
                last_name=last_name
            )
            # Generate a verification token
            token = default_token_generator.make_token(user)

            # Build the verification URL
            current_site = get_current_site(request)
            verification_url = reverse('verify_email', args=[urlsafe_base64_encode(force_bytes(user.pk)), token])
            verification_url = f'http://{current_site.domain}{verification_url}'

            # Send the verification email
            subject = 'Verify your email address'
            message = f'Click the following link to verify your Account: {verification_url}'
            from_email = settings.DEFAULT_FROM_EMAIL  # Set your email here
            to_email = [user.email]
            send_mail(subject, message, from_email, to_email, fail_silently=False)

            # Update the Account model or set a flag indicating that the verification email has been sent

            # Redirect to the success page with email parameter
            redirect_url = redirect('sent_verification')
            if wmsu_email:
                redirect_url['Location'] += f'?email={wmsu_email}'
            return redirect_url
        except ValidationError as e:
            error_messages['general'] = str(e)
            print(f'Validation Error: {e}')
        except Exception as ex:
            error_messages['general'] = f'Error Creating Account: {ex}'
            print(f'Error Creating Account: {ex}')

        return render(request, 'login/signup.html', {'error_messages': error_messages})

    return render(request, 'login/signup.html')


def logout(request):
    auth.logout(request)
    return redirect('login')

@login_required
def userpage_view (request):
    return render(request, 'user/userpage.html')

@login_required
def settings_view (request):
    return render(request, 'user/settings.html')

@login_required
def custom_password_change_view(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return JsonResponse({'success': True})
        else:
            messages.error(request, 'Please correct the error below.')
            errors = dict(form.errors)
            return JsonResponse({'success': False, 'errors': errors})

    return render(request, 'user/settings.html')
# ---------------------------- SYLLABUS TEMPLATE --------------------------------
@login_required
def templates_list(request):
    # templates = get_object_or_404(Syllabus_Template, user_id=request.user)
    if request.user.is_authenticated:
            # If the user is authenticated, use their account for the syllabus input
            account = request.user
    else:
        # Handle the case where the user is not logged in or not authenticated
        return render(request, 'https://media.tenor.com/-YlzaY7PXb4AAAAd/among-us-amogus.gif')

    templates = Syllabus_Template.objects.filter(user_id=account)

    return render(request, 'user/template/templates-list.html', {'templates': templates})

# ---------- SETUP SYLLABUS TEMPLATE ----------
@login_required
def new_template(request):
    # Default Values
    vision = Vision.objects.get(default = True)
    mission = Mission.objects.get(default = True)
    mission_itemizes = Mission_Itemize.objects.filter(default=True)
    percentage_grade_range = Percentage_Grade_Range.objects.filter(default=True)

    if request.method == 'POST':
        # Initialize an empty dictionary to store error messages
        error_messages = {}

        # ----- Syllabus Template -----
        name = request.POST['name']

        # if user didn't enter name for their template
        if not name:
            # Query to find the count of existing templates for the user
            template_count = Syllabus_Template.objects.filter(user_id=request.user).aggregate(Count('id'))['id__count']
            next_template_number = template_count + 1
            name = f'Template {next_template_number}'

        syllabus_template = Syllabus_Template(user_id = request.user, name = name)
        syllabus_template.save()

        # ----- Logo -----
        form = LogoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Process and save each uploaded logo name and file
            for field_name, uploaded_file in request.FILES.items():
                # Check if the file input is not empty
                if uploaded_file:
                    img_name = uploaded_file.name

                    # Build the destination path using MEDIA_ROOT and the desired folder structure
                    destination_path = os.path.join(settings.MEDIA_ROOT, 'logo', img_name)

                    # Save the uploaded image to the destination folder
                    with open(destination_path, 'wb+') as destination:
                        for chunk in uploaded_file.chunks():
                            destination.write(chunk)

                    # Store the image name in the database
                    logo = Logo(syllabus_template_id=syllabus_template, name=field_name, img_name=os.path.join('logo', img_name))
                    logo.save()

        # ----- Vision -----
        new_vision = request.POST['vision']

        vision = Vision(syllabus_template_id=syllabus_template, vision=new_vision) # create new vision record
        vision.save()

        # ----- Vision Itemize -----
        vision_itemize_values = request.POST.getlist('vision_itemize') # Get a list of values from the form inputs

        # Iterate through the values and save them to the database
        for value in vision_itemize_values:
            vision_itemize = Vision_Itemize(syllabus_template_id=syllabus_template, vision_itemize=value)
            vision_itemize.save()

        # ----- Mission -----
        new_mission = request.POST['mission']

        mission = Mission(syllabus_template_id=syllabus_template, mission=new_mission)
        mission.save()

        # ----- Mission Itemize -----
        mission_itemize_values = request.POST.getlist('mission_itemize')

        for value in mission_itemize_values:
            mission_itemize = Mission_Itemize(syllabus_template_id=syllabus_template, mission_itemize=value)
            mission_itemize.save()

        # ----- Goal -----
        goal_value = request.POST['goal']

        goal = Goal(syllabus_template_id=syllabus_template, goal=goal_value)
        goal.save()

        # -----Goal Itemize -----
        goal_itemize_values = request.POST.getlist('goal_itemize')

        for value in goal_itemize_values:
            goal_itemize = Goal_Itemize(syllabus_template_id=syllabus_template, goal_itemize=value)
            goal_itemize.save()

        # ----- Course Outcome -----
        course_outcome_values = request.POST.getlist('course_outcome')
        for value in course_outcome_values:
            course_outcome = Course_Outcome(syllabus_template_id=syllabus_template, course_outcome=value.capitalize())
            course_outcome.save()

        # ---------- Grading System ----------
        grading_system_type = request.POST['grading_system_type']
        grading_system = Grading_System(syllabus_template_id=syllabus_template, grading_system_type=grading_system_type) # create grading system table
        grading_system.save()

        # ----- Midterm -----
        midterm_grade_value = request.POST['midterm-grade']
        if not midterm_grade_value: midterm_grade_value = 0 # if percentage is empty

        midterm = Term_Grade(grading_system_id=grading_system, term_name='midterm', term_percentage=midterm_grade_value)
        midterm.save() # create and store values for midterm

        if grading_system_type == 'lecture only':
            add_grading_system(midterm, 'midterm', 'lecture', request, False)

        elif grading_system_type == 'laboratory only':
            add_grading_system(midterm, 'midterm', 'laboratory', request, False)

        else: # for both lecture and laboratory
            add_grading_system(midterm, 'midterm', 'lecture', request, False)
            add_grading_system(midterm, 'midterm', 'laboratory', request, False)

        # ----- Finalterm -----
        finalterm_grade_value = request.POST['finalterm-grade']
        if not finalterm_grade_value: finalterm_grade_value = 0 # if percentage is empty

        finalterm = Term_Grade(grading_system_id=grading_system, term_name='finalterm', term_percentage=finalterm_grade_value)
        finalterm.save() # create and store values for finalterm

        if grading_system_type == 'lecture only':
            add_grading_system(finalterm, 'finalterm', 'lecture', request, False)

        elif grading_system_type == 'laboratory only':
            add_grading_system(finalterm, 'finalterm', 'laboratory', request, False)

        else: # for both lecture and laboratory
            add_grading_system(finalterm, 'finalterm', 'lecture', request, False)
            add_grading_system(finalterm, 'finalterm', 'laboratory', request, False)

        # ----- Percentage Grade Range -----
        min_range_values = request.POST.getlist('min-range')
        max_range_values = request.POST.getlist('max-range')
        grade_values = request.POST.getlist('grade')

        for min, max, grade in zip(min_range_values, max_range_values, grade_values):
            # if value is empty
            if not min: min = 0
            if not max: max = 0
            if not grade: grade = 0

            percentage_grade_range = Percentage_Grade_Range(
                grading_system_id = grading_system,
                min_range = min,
                max_range = max,
                grade = grade
            )
            percentage_grade_range.save()

        return redirect('templates_list') # redirect to list of templates


    form = LogoUploadForm() # form for uploading logo

    return render(request, 'user/template/new_template.html',
                  {
                        'form': form,
                        'vision': vision,
                        'mission': mission,
                        'mission_itemizes': mission_itemizes,
                        'percentage_grade_ranges': percentage_grade_range
                  })

@login_required
def edit_template(request, id):
    syllabus_template = get_object_or_404(Syllabus_Template, user_id=request.user, id=id)
    logos = Logo.objects.filter(syllabus_template_id=syllabus_template)

    vision = Vision.objects.get(syllabus_template_id=syllabus_template)
    vision_itemize = Vision_Itemize.objects.filter(syllabus_template_id=syllabus_template)
    mission = Mission.objects.get(syllabus_template_id=syllabus_template)
    mission_itemize = Mission_Itemize.objects.filter(syllabus_template_id=syllabus_template)

    goal = Goal.objects.get(syllabus_template_id=syllabus_template)
    goal_itemize = Goal_Itemize.objects.filter(syllabus_template_id=syllabus_template)

    course_outcome = Course_Outcome.objects.filter(syllabus_template_id=syllabus_template)

    grading_system = Grading_System.objects.get(syllabus_template_id=syllabus_template)
    midterm = Term_Grade.objects.get(grading_system_id=grading_system, term_name="midterm")
    midterm_lecture = Term_Description.objects.filter(term_grade_id=midterm, lecture_percentage__isnull=False)
    midterm_laboratory = Term_Description.objects.filter(term_grade_id=midterm, laboratory_percentage__isnull=False)
    finalterm = Term_Grade.objects.get(grading_system_id=grading_system, term_name="finalterm")
    finalterm_lecture = Term_Description.objects.filter(term_grade_id=finalterm, lecture_percentage__isnull=False)
    finalterm_laboratory = Term_Description.objects.filter(term_grade_id=finalterm, laboratory_percentage__isnull=False)
    percentage_grade_range = Percentage_Grade_Range.objects.filter(grading_system_id=grading_system)

    if 'delete' in request.POST:
        syllabus_template.delete()
        return redirect('templates_list')

    elif 'edit' in request.POST:
        name = request.POST['name']

        if not name:
            # Query to find the count of existing templates for the user
            template_count = Syllabus_Template.objects.filter(user_id=request.user).aggregate(Count('id'))['id__count']
            name = f'Template {template_count}'

        syllabus_template.name = name
        syllabus_template.save()

        # ----- LOGOS -----
        form = LogoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Process and save each uploaded logo name and file
            for field_name, uploaded_file in request.FILES.items():
                # Check if the file input is not empty
                if uploaded_file:
                    try:
                        # Attempt to get existing logo
                        logo = Logo.objects.get(syllabus_template_id=syllabus_template, name=field_name)
                    except Logo.DoesNotExist:
                        # Logo doesn't exist, create a new one
                        logo = Logo(syllabus_template_id=syllabus_template, name=field_name)
                    else:
                        # Logo exists, delete the old image file
                        old_img_path = os.path.join(settings.MEDIA_ROOT, logo.img_name)
                        if os.path.exists(old_img_path):
                            os.remove(old_img_path)

                    # Process and save the uploaded image
                    img_name = uploaded_file.name
                    destination_path = os.path.join(settings.MEDIA_ROOT, 'logo', img_name)

                    with open(destination_path, 'wb+') as destination:
                        for chunk in uploaded_file.chunks():
                            destination.write(chunk)

                    # Update the logo information in the database
                    logo.img_name = os.path.join('logo', img_name)
                    logo.save()

        vision.vision = request.POST['vision']
        vision.save()

        vision_itemize.delete()
        vision_itemize_values = request.POST.getlist('vision_itemize')
        for value in vision_itemize_values:
            vision_itemize = Vision_Itemize(syllabus_template_id=syllabus_template, vision_itemize=value)
            vision_itemize.save()

        mission.mission = request.POST['mission']
        mission.save()

        mission_itemize.delete()
        mission_itemize_values = request.POST.getlist('mission_itemize')
        for value in mission_itemize_values:
            mission_itemize = Mission_Itemize(syllabus_template_id=syllabus_template, mission_itemize=value)
            mission_itemize.save()

        goal.goal = request.POST['goal']
        goal.save()

        goal_itemize.delete()
        goal_itemize_values = request.POST.getlist('goal_itemize')
        for value in goal_itemize_values:
            goal_itemize = Goal_Itemize(syllabus_template_id=syllabus_template, goal_itemize=value)
            goal_itemize.save()

        course_outcome.delete()
        course_outcome_values = request.POST.getlist('course_outcome')
        for value in course_outcome_values:
            course_outcome = Course_Outcome(syllabus_template_id=syllabus_template, course_outcome=value.capitalize())
            course_outcome.save()

        grading_system_type = request.POST['grading_system_type']
        grading_system.grading_system_type = grading_system_type
        grading_system.save()

        midterm_grade_value = request.POST['midterm-grade']
        if not midterm_grade_value: midterm_grade_value = 0 # if percentage is empty

        midterm.term_percentage = midterm_grade_value
        midterm.save()

        midterm_lecture.delete()
        midterm_laboratory.delete()
        if grading_system_type == 'lecture only':
            add_grading_system(midterm, 'midterm', 'lecture', request, False)

        elif grading_system_type == 'laboratory only':
            add_grading_system(midterm, 'midterm', 'laboratory', request, False)

        else: # for bothe lecture and laboratory
            add_grading_system(midterm, 'midterm', 'lecture', request, False)
            add_grading_system(midterm, 'midterm', 'laboratory', request, False)

        finalterm_grade_value = request.POST['finalterm-grade']
        if not finalterm_grade_value: finalterm_grade_value = 0 # if percentage is empty

        finalterm.term_percentage = finalterm_grade_value
        finalterm.save()

        finalterm_lecture.delete()
        finalterm_laboratory.delete()
        if grading_system_type == 'lecture only':
            add_grading_system(finalterm, 'finalterm', 'lecture', request, False)

        elif grading_system_type == 'laboratory only':
            add_grading_system(finalterm, 'finalterm', 'lecture', request, False)

        else: # for both lecture and laboratory
            add_grading_system(finalterm, 'finalterm', 'lecture', request, False)
            add_grading_system(finalterm, 'finalterm', 'laboratory', request, False)

        percentage_grade_range.delete()
        min_range_values = request.POST.getlist('min-range')
        max_range_values = request.POST.getlist('max-range')
        grade_values = request.POST.getlist('grade')
        for min, max, grade in zip(min_range_values, max_range_values, grade_values):
            # if value is empty
            if not min:
                min = 0

            if not max:
                max = 0

            if not grade:
                grade = 0

            percentage_grade_range = Percentage_Grade_Range(
                grading_system_id = grading_system,
                min_range = min,
                max_range = max,
                grade = grade
            )
            percentage_grade_range.save()

        return redirect('templates_list')

    form = LogoUploadForm() # form for uploading logo

    return render(request, 'user/template/edit_template.html', {
        'syllabus_template': syllabus_template,
        'logos': logos,
        'vision': vision,
        'vision_itemizes': vision_itemize,
        'mission': mission,
        'mission_itemizes': mission_itemize,
        'goal': goal,
        'goal_itemizes': goal_itemize,
        'course_outcomes': course_outcome,
        'grading_system': grading_system,
        'midterm': midterm,
        'midterm_lectures': midterm_lecture,
        'midterm_laboratories': midterm_laboratory,
        'finalterm': finalterm,
        'finalterm_lectures': finalterm_lecture,
        'finalterm_laboratories': finalterm_laboratory,
        'percentage_grade_ranges': percentage_grade_range,
        'form': form,
    })

# ------------------------------------------------------------

@login_required
def new_syllabus(request):
    syllabus_template = Syllabus_Template.objects.filter(user_id=request.user)
    default_percentage_grade_range = Percentage_Grade_Range.objects.filter(default=True)

    if request.method == 'POST':
        syllabus_name = request.POST['syllabus-name']

        if not syllabus_name: # if user didn't enter name for their template, it will automatically store a value
            syllabus_count = Syllabus.objects.filter(user_id=request.user).aggregate(Count('id'))['id__count']
            syllabus_name = f'Syllabus {syllabus_count + 1}'


        syllabus = Syllabus(user_id=request.user, syllabus_name=syllabus_name)
        syllabus_template = Syllabus_Template.objects.get(id=request.POST['template'])

        syllabus.syllabus_template_id = syllabus_template
        syllabus.time_frame = request.POST['time-frame']
        syllabus.college = request.POST['college'].title()
        syllabus.department = request.POST['department'].upper()
        syllabus.bachelor = request.POST['bachelor'].title()

        # ----- SUBJECT COURSE -----
        syllabus.course_code = request.POST['course-code']
        syllabus.course_name = request.POST['course-name']
        course_credit = request.POST['course-credit']
        if not course_credit: course_credit = 3.0
        syllabus.course_credit = course_credit
        syllabus.course_credit_description = request.POST['course_credit_description']
        syllabus.course_description = request.POST['course-description']
        syllabus.save()

        # ----- PRERIQUISITE -----
        preriquisite_values = request.POST.getlist('preriquisite')
        for value in preriquisite_values:
            if value:
                preriquisite = Preriquisite(syllabus_id=syllabus, preriquisite=value)
                preriquisite.save()

        # ----- GRADING SYSTEM -----
        grading_system_option = request.POST['grading_system_option']
        syllabus.grading_system_option = grading_system_option
        syllabus.save()

        if grading_system_option == 'create-new':
            grading_system_type = request.POST['grading_system_type'] # will be use for prompting

            grading_system = Syllabus_Grading_System(syllabus_id=syllabus, grading_system_type=grading_system_type)
            grading_system.save()

            # ----- Midterm -----
            midterm_grade_value = request.POST['midterm-grade']
            if not midterm_grade_value: midterm_grade_value = 0  # if percentage is empty

            midterm = Syllabus_Term_Grade(grading_system_id=grading_system, term_name='midterm', term_percentage=midterm_grade_value)
            midterm.save() # create and store values for midterm

            if grading_system_type == 'lecture only':
                add_grading_system(midterm, 'midterm', 'lecture', request, True)

            elif grading_system_type == 'laboratory only':
                add_grading_system(midterm, 'midterm', 'laboratory', request, True)

            else: # for both lecture and laboratory
                add_grading_system(midterm, 'midterm', 'lecture', request, True)
                add_grading_system(midterm, 'midterm', 'laboratory', request, True)

            # ----- Finalterm -----
            finalterm_grade_value = request.POST['finalterm-grade']
            if not finalterm_grade_value: finalterm_grade_value = 0 # if percentage is empty

            finalterm = Syllabus_Term_Grade(grading_system_id=grading_system, term_name='finalterm', term_percentage=finalterm_grade_value)
            finalterm.save() # create and store values for finalterm

            if grading_system_type == 'lecture only':
                add_grading_system(finalterm, 'finalterm', 'lecture', request, True)

            elif grading_system_type == 'laboratory only':
                add_grading_system(finalterm, 'finalterm', 'laboratory', request, True)

            else: # for both lecture and laboratory
                add_grading_system(finalterm, 'finalterm', 'lecture', request, True)
                add_grading_system(finalterm, 'finalterm', 'laboratory', request, True)

            # ----- Percentage Grade Range -----
            min_range_values = request.POST.getlist('min-range')
            max_range_values = request.POST.getlist('max-range')
            grade_values = request.POST.getlist('grade')

            for min, max, grade in zip(min_range_values, max_range_values, grade_values):
                # if value is empty
                if not min: min = 0
                if not max: max = 0
                if not grade: grade = 0

                percentage_grade_range = Syllabus_Percentage_Grade_Range(
                    grading_system_id=grading_system,
                    min_range = min,
                    max_range = max,
                    grade = grade
                )
                percentage_grade_range.save()

        else:
            template_gs = Grading_System.objects.get(syllabus_template_id=syllabus_template)
            template_mt = Term_Grade.objects.get(grading_system_id=template_gs, term_name="midterm")
            template_mt_lecs = Term_Description.objects.filter(term_grade_id=template_mt, lecture_percentage__isnull=False)
            template_mt_labs = Term_Description.objects.filter(term_grade_id=template_mt, laboratory_percentage__isnull=False)
            template_ft = Term_Grade.objects.get(grading_system_id=template_gs, term_name="finalterm")
            template_ft_lecs = Term_Description.objects.filter(term_grade_id=template_ft, lecture_percentage__isnull=False)
            template_ft_labs = Term_Description.objects.filter(term_grade_id=template_ft, laboratory_percentage__isnull=False)
            template_pgrs = Percentage_Grade_Range.objects.filter(grading_system_id=template_gs)

            grading_system = Syllabus_Grading_System(syllabus_id=syllabus, grading_system_type=template_gs.grading_system_type)
            grading_system.save()

            # ----- Midterm -----
            midterm = Syllabus_Term_Grade(grading_system_id=grading_system, term_name='midterm', term_percentage=template_mt.term_percentage)
            midterm.save() # create and store values for midterm

            if grading_system.grading_system_type == 'lecture only':
                for template_mt_lec in template_mt_lecs:
                    term_description = Syllabus_Term_Description(term_grade_id=midterm,
                                                                 term_description=template_mt_lec.term_description,
                                                                 percentage=template_mt_lec.percentage,
                                                                 lecture_percentage=template_mt_lec.lecture_percentage)
                    term_description.save()

            elif grading_system.grading_system_type == 'laboratory only':
                for template_mt_lab in template_mt_labs:
                    term_description = Syllabus_Term_Description(term_grade_id=midterm,
                                                                 term_description=template_mt_lab.term_description,
                                                                 percentage=template_mt_lab.percentage,
                                                                 laboratory_percentage=template_mt_lab.laboratory_percentage)
                    term_description.save()

            else: # for both lecture and laboratory
                for template_mt_lec in template_mt_lecs:
                    term_description = Syllabus_Term_Description(term_grade_id=midterm,
                                                                 term_description=template_mt_lec.term_description,
                                                                 percentage=template_mt_lec.percentage,
                                                                 lecture_percentage=template_mt_lec.lecture_percentage)
                    term_description.save()

                for template_mt_lab in template_mt_labs:
                    term_description = Syllabus_Term_Description(term_grade_id=midterm,
                                                                 term_description=template_mt_lab.term_description,
                                                                 percentage=template_mt_lab.percentage,
                                                                 laboratory_percentage=template_mt_lab.laboratory_percentage)
                    term_description.save()

            # ----- Finalterm -----
            finalterm = Syllabus_Term_Grade(grading_system_id=grading_system, term_name='finalterm', term_percentage=template_ft.term_percentage)
            finalterm.save() # create and store values for finalterm

            if grading_system.grading_system_type == 'lecture only':
                for template_ft_lec in template_ft_lecs:
                    term_description = Syllabus_Term_Description(term_grade_id=finalterm,
                                                                 term_description=template_ft_lec.term_description,
                                                                 percentage=template_ft_lec.percentage,
                                                                 lecture_percentage=template_ft_lec.lecture_percentage)
                    term_description.save()

            elif grading_system.grading_system_type == 'laboratory only':
                for template_ft_lab in template_ft_labs:
                    term_description = Syllabus_Term_Description(term_grade_id=finalterm,
                                                                 term_description=template_ft_lab.term_description,
                                                                 percentage=template_ft_lab.percentage,
                                                                 laboratory_percentage=template_ft_lab.laboratory_percentage)
                    term_description.save()

            else: # for both lecture and laboratory
                for template_ft_lec in template_ft_lecs:
                    term_description = Syllabus_Term_Description(term_grade_id=finalterm,
                                                                 term_description=template_ft_lec.term_description,
                                                                 percentage=template_ft_lec.percentage,
                                                                 lecture_percentage=template_ft_lec.lecture_percentage)
                    term_description.save()

                for template_ft_lab in template_ft_labs:
                    term_description = Syllabus_Term_Description(term_grade_id=finalterm,
                                                                 term_description=template_ft_lab.term_description,
                                                                 percentage=template_ft_lab.percentage,
                                                                 laboratory_percentage=template_ft_lab.laboratory_percentage)
                    term_description.save()


            # ----- Percentage Grade Range -----
            for template_pgr in template_pgrs:
                percentage_grade_range = Syllabus_Percentage_Grade_Range(
                    grading_system_id=grading_system,
                    min_range = template_pgr.min_range,
                    max_range = template_pgr.max_range,
                    grade = template_pgr.grade
                )

                percentage_grade_range.save()

            grading_system_type = grading_system.grading_system_type

        # ----- REFERENCES -----
        source_type = request.POST['syllabus-source-type']
        syllabus.source_type = source_type
        syllabus.save()

        syllabus_ai = Syllabus_AI(user_id=request.user)
        syllabus_ai.save()


        # ----- ACADEMIC YEAR -----
        syllabus.semester = request.POST['semester']
        syllabus.school_year = request.POST['school-year']
        syllabus.save()

        # ----- COURSE REQUIREMENTS -----
        course_requirement_values = request.POST.getlist('course-requirements')

        for value in course_requirement_values:
            course_requirements = Course_Requirements(syllabus_id=syllabus, requirements=value)
            course_requirements.save()

        # ----- PERSONELS -----
        prepared_name_values = request.POST.getlist('prepared-name')

        for name in prepared_name_values:
            prepared = Prepared(syllabus_id=syllabus, fullname=name)
            prepared.save()

        syllabus.recommending_approval_name = request.POST['recommending-approval-name']
        syllabus.recommending_approval_position = request.POST['recommending-approval-position']
        syllabus.concured_name = request.POST['concured-name']
        syllabus.concured_position = request.POST['concured-position']
        syllabus.approved_name = request.POST['approved-name']
        syllabus.approved_position = request.POST['approved-position']

        # ----- MORE INFO -----
        syllabus.footer_info = request.POST['footer-info']

        effective_date = request.POST['effective-date']
        if not effective_date: effective_date = timezone.now().date()
        syllabus.effective_date = effective_date

        syllabus.save()

        language = request.POST.get('language')
        syllabus_ai.language=language
        syllabus_ai.save()

        # ---------- OPENAI PROMPTING, RECIEVING AND STORING DATA ----------
        if source_type == 'auto':
            # ----- GENERATE REFERENCES, TOPICS AND LEARNING OUTCOMES -----
            while  True:
                try:
                    prompt = 'Speak in this language:'+ syllabus_ai.language + '.' + syllabus.course_name + ' "' + syllabus.course_description + '" please generate 5 popular and existing references in ' + grading_system_type + ' type for exactly ' + syllabus.time_frame + ' weeks\' time frame ALWAYS INCLUDE THE YEAR OF THE REFERENCES. Each should be separated by "|". Then extract a comprehensive range of significant and pertinent 10-16 topics from the reference sources that align with the objectives of the 18-week time frame, feel free to suggest any additional areas of focus or related subjects that may enhance the depth and breadth of the content, separate each topic by "|". Then after, generate 7 exact course learning outcomes or what should student accomplish based on all information provided and you will provide. Do not explain, comment, add labels, foot notes, no break lines, empty lines, do not provide in a list, no number list or other ordered number format. Provide information right away in single line and in normal style and font style. Use this format: source1 | source2 | and so on || topic1 | topic2 | and so on || course learning outcome1 | course learning outcome2 | and so on. Sample output: "A Theory of Islamic Finance" by Muhammad Nejatullah Siddiqi (1983) | "Islamic Banking and Interest: A Study of the Prohibition of Riba and Its Contemporary Interpretation" by Waheeduddeen Ahmed (1996) || Introduction to OOP principles | Classes and Objects || Design and implement object-oriented programs using Java | Demonstrate proficiency in using inheritance and polymorphism. (Do not put extra "||" at the very end)'
                    response = ask_openai(prompt)

                    syllabus_ai.raw_first_prompt = prompt
                    syllabus_ai.raw_first_response = response
                    syllabus_ai.save()
                    raw_sources, raw_topics, raw_learning_outcomes = response.split('||')

                    break

                except ValueError as e:
                    continue

            syllabus_ai.raw_source=raw_sources
            syllabus_ai.raw_topics=raw_topics
            syllabus_ai.raw_course_learning_outcomes=raw_learning_outcomes

            syllabus.syllabus_ai_id = syllabus_ai
            syllabus.save()


            # ----- PROCESS RAW SOURCES -----
            raw_sources = raw_sources.strip().split('|')

            for source in raw_sources:
                sources = Sources(syllabus_ai_id=syllabus_ai, reference=source)
                sources.save()

            # ----- PROCESS RAW topics-----
            raw_topics = re.split(r'[-*,A-Za-z0-9]\.\s*|\|', raw_topics)

            for topic in raw_topics:
                topics = Topic(syllabus_ai_id=syllabus_ai, topic_name=topic )
                topics.save()

            # ----- PROCESS RAW LEARNING OUTCOMES -----
            learning_outcomes = raw_learning_outcomes.strip().split('|')
            letter_counter = ord('A')
            learning_outcomes_cont = ""

            for learning_outcome in learning_outcomes:
                course_learning_outcome = Course_Learning_Outcome(syllabus_ai_id=syllabus_ai, course_learning_outcome=learning_outcome)
                course_learning_outcome.save()

                learning_outcomes_cont += f"{chr(letter_counter)}. {learning_outcome.strip()} | "
                letter_counter += 1

            learning_outcomes = learning_outcomes_cont[:-3]
            syllabus_ai.raw_course_learning_outcomes_ai_with_letters = learning_outcomes
            syllabus_ai.save()

        elif source_type == 'specific':
            sources_values = request.POST.getlist('source[]')
            join_specific_sources = ", ".join(sources_values)  # Join the source names with commas

            # ----- GENERATE REFERENCES, TOPICS AND LEARNING OUTCOMES -----
            raw_sources = join_specific_sources
            raw_topics =ask_openai('Speak in this language:'+ syllabus_ai.language + '.Based on this references: '+ join_specific_sources +'. "' + grading_system_type + '" and based on what type of subject. Get all the topics that can be get. Do not explain, Do not comment, Do not add empty lines, respond with single line with this format. (topic 1| topic 2 | topic 3). Finish until it is done. Do not put inside a parentheses.Do not forget to use the "|" to separate. Give at least 18 topics. Minimum of topics is 18. Do not duplicate topics.')

            raw_learning_outcomes =ask_openai('Speak in this language:'+ syllabus_ai.language + '.Based on these topics ' + raw_topics + ', generate the course learning outcomes. Separate everything using "|" or use a vertical line. Do not explain, Do not comment, Do not add empty lines, respond with a single line. Repeat until it is done. Do not add parentheses.')


            syllabus_ai.raw_source=raw_sources
            syllabus_ai.raw_topics=raw_topics
            syllabus_ai.raw_course_learning_outcomes=raw_learning_outcomes
            syllabus_ai.save()

            syllabus.syllabus_ai_id = syllabus_ai
            syllabus.save()


            # ----- PROCESS RAW SOURCES -----
            raw_sources = raw_sources.strip().split('|')

            for value in sources_values:
                source = Sources(syllabus_ai_id=syllabus_ai, reference=value)
                source.save()

            # ----- PROCESS RAW topics-----
            raw_topics = re.split(r'[-*,A-Za-z0-9]\.\s*|\|', raw_topics)

            for topic in raw_topics:
                topics = Topic(syllabus_ai_id=syllabus_ai, topic_name=topic )
                topics.save()

            # ----- PROCESS RAW LEARNING OUTCOMES -----
            learning_outcomes = re.split(r'[-*A-Za-z0-9]\.\s*|\|', raw_learning_outcomes)
            letter_counter = ord('A')
            learning_outcomes_cont = ""

            for learning_outcome in learning_outcomes:
                course_learning_outcome = Course_Learning_Outcome(syllabus_ai_id=syllabus_ai, course_learning_outcome=learning_outcome)
                course_learning_outcome.save()

                learning_outcomes_cont += f"{chr(letter_counter)}. {learning_outcome.strip()} | "
                letter_counter += 1

            learning_outcomes = learning_outcomes_cont[:-3]
            syllabus_ai.raw_course_learning_outcomes_ai_with_letters = learning_outcomes
            syllabus_ai.save()

        return redirect('show_syllabus_first', id=syllabus_ai.id)  # redirect to edit page


    return render(request, 'user/ai_syllabus/new_syllabus.html', {'syllabus_templates': syllabus_template, 'percentage_grade_ranges': default_percentage_grade_range})

@login_required
def edit_syllabus(request, id):
    # Retrieve the specific syllabus_ai_input object based on the provided id
    # ----- SYLLABUS -----
    syllabus = get_object_or_404(Syllabus, user_id=request.user, id=id)
    preriquisite = Preriquisite.objects.filter(syllabus_id=syllabus)
    course_requirements = Course_Requirements.objects.filter(syllabus_id=syllabus)
    prepared = Prepared.objects.filter(syllabus_id=syllabus)

    # ----- GRADING SYSTEM -----
    grading_system = Syllabus_Grading_System.objects.get(syllabus_id=syllabus)
    midterm = Syllabus_Term_Grade.objects.get(grading_system_id=grading_system, term_name='midterm')
    midterm_lecture = Syllabus_Term_Description.objects.filter(term_grade_id=midterm, lecture_percentage__isnull=False)
    midterm_laboratory = Syllabus_Term_Description.objects.filter(term_grade_id=midterm, laboratory_percentage__isnull=False)
    finalterm = Syllabus_Term_Grade.objects.get(grading_system_id=grading_system, term_name='finalterm')
    finalterm_lecture = Syllabus_Term_Description.objects.filter(term_grade_id=finalterm, lecture_percentage__isnull=False)
    finalterm_laboratory = Syllabus_Term_Description.objects.filter(term_grade_id=finalterm, laboratory_percentage__isnull=False)
    percentage_grade_range = Syllabus_Percentage_Grade_Range.objects.filter(grading_system_id=grading_system)

    # ----- SYLLABUS AI -----
    syllabus_ai = get_object_or_404(Syllabus_AI, user_id=request.user, id=syllabus.syllabus_ai_id.id)
    print(syllabus_ai)
    # ----- SYLLABUS TEMPLATE -----
    syllabus_template = get_object_or_404(Syllabus_Template, user_id=request.user, id=syllabus.syllabus_template_id.id)
    syllabus_templates = Syllabus_Template.objects.filter(user_id=request.user)

    if 'delete' in request.POST:
        syllabus.delete()
        return redirect('userpage')

    elif 'edit' in request.POST:
        # ----- REUSABLE FUNCTION -----
        def check_and_update(model, fields):
            for field in fields:
                new_value = request.POST.get(field)

                if new_value is not None and new_value != getattr(model, field):
                    setattr(model, field, new_value)
                    model.save()

        syllabus_template = Syllabus_Template.objects.get(id=request.POST['template'])

        # ----- SYLLABUS -----
        syllabus.syllabus_template_id = syllabus_template
        syllabus.save()

        fields = ['syllabus_name', 'college', 'department', 'bachelor', 'course_code', 'course_name', 'course_credit', 'course_credit_description', 'course_description', 'semester', 'school_year',
                  'recommending_approval_name', 'recommending_approval_position', 'concured_name', 'concured_position', 'approved_name', 'approved_position', 'footer_info', 'effective_date']

        check_and_update(syllabus, fields)

        # ----- SYLLABUS_AI -----
        language = request.POST.get('language')
        if language and language != syllabus_ai.language:
            syllabus_ai.language = language
            syllabus_ai.save()

        print("Language:", syllabus_ai.language)

        # ----- SYLLABUS CONTENT -----
        preriquisite.delete()
        preriquisite_values = request.POST.getlist('preriquisite')
        for value in preriquisite_values:
            preriquisite = Preriquisite(syllabus_id=syllabus, preriquisite=value)
            preriquisite.save()

        course_requirements.delete()
        course_requirements_values = request.POST.getlist('course-requirements')
        for value in course_requirements_values:
            course_requirement = Course_Requirements(syllabus_id=syllabus, requirements=value)
            course_requirement.save()

        prepared.delete()
        prepared_values = request.POST.getlist('prepared-name')
        for value in prepared_values:
            prepared = Prepared(syllabus_id=syllabus, fullname=value)
            prepared.save()

        # ----- GRADING SYSTEM -----
        grading_system_type = request.POST['grading_system_type']
        grading_system.delete()

        grading_system = Syllabus_Grading_System(syllabus_id=syllabus, grading_system_type=grading_system_type)
        grading_system.save()

        midterm_grade_value = request.POST['midterm-grade']
        finalterm_grade_value = request.POST['finalterm-grade']
        if not midterm_grade_value: midterm_grade_value = 0
        if not finalterm_grade_value: finalterm_grade_value = 0

        midterm = Syllabus_Term_Grade(grading_system_id=grading_system, term_name='midterm', term_percentage=midterm_grade_value)
        midterm.save()

        if grading_system_type == 'lecture only':
            add_grading_system(midterm, 'midterm', 'lecture', request, True)

        elif grading_system_type == 'laboratory only':
            add_grading_system(midterm, 'midterm', 'laboratory', request, True)

        else: # for both lecture and laboratory
            add_grading_system(midterm, 'midterm', 'lecture', request, True)
            add_grading_system(midterm, 'midterm', 'laboratory', request, True)

        finalterm = Syllabus_Term_Grade(grading_system_id=grading_system, term_name='finalterm', term_percentage=finalterm_grade_value)
        finalterm.save()

        if grading_system_type == 'lecture only':
            add_grading_system(finalterm, 'finalterm', 'lecture', request, True)

        elif grading_system_type == 'laboratory only':
            add_grading_system(finalterm, 'finalterm', 'laboratory', request, True)

        else: # for both lecture and laboratory
            add_grading_system(finalterm, 'finalterm', 'lecture', request, True)
            add_grading_system(finalterm, 'finalterm', 'laboratory', request, True)

        min_range_values = request.POST.getlist('min-range')
        max_range_values = request.POST.getlist('max-range')
        grade_values = request.POST.getlist('grade')
        for min, max, grade in zip(min_range_values, max_range_values, grade_values):
            # if value is empty
            if not min:
                min = 0

            if not max:
                max = 0

            if not grade:
                grade = 0

            percentage_grade_range = Syllabus_Percentage_Grade_Range(
                grading_system_id = grading_system,
                min_range = min,
                max_range = max,
                grade = grade
            )
            percentage_grade_range.save()

        return redirect('edit_syllabus', id=id)

    # Pass the data to the template
    context = {
        'syllabus': syllabus,
        'syllabus_ai': syllabus_ai,
        'preriquisites': preriquisite,
        'course_requirements': course_requirements,
        'prepares': prepared,
        'grading_system': grading_system,
        'midterm': midterm,
        'midterm_lectures': midterm_lecture,
        'midterm_laboratories': midterm_laboratory,
        'finalterm': finalterm,
        'finalterm_lectures': finalterm_lecture,
        'finalterm_laboratories': finalterm_laboratory,
        'percentage_grade_ranges': percentage_grade_range,
        'syllabus_template': syllabus_template,
        'syllabus_templates': syllabus_templates,
    }

    return render(request, 'user/ai_syllabus/edit_syllabus.html', context)


class SyllabusView1(TemplateView):
    template_name = 'user/ai_syllabus/show_info1.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        id = kwargs['id']  # Retrieve the 'id' parameter from the URL

        syllabus_ai = get_object_or_404(Syllabus_AI, id=id) # HERE -----
        references = Sources.objects.filter(syllabus_ai_id=syllabus_ai) # HERE -----
        topics = Topic.objects.filter(syllabus_ai_id=syllabus_ai) # HERE -----
        course_learning_outcomes = Course_Learning_Outcome.objects.filter(syllabus_ai_id=syllabus_ai) # HERE -----

        syllabus = Syllabus.objects.get(syllabus_ai_id=syllabus_ai)  # HERE -----

        context['syllabus'] = syllabus # HERE -----
        context['syllabus_ai'] = syllabus_ai # HERE -----
        context['references'] = references
        context['topics'] = topics
        context['course_learning_outcomes'] = course_learning_outcomes

        return context

class AddReference(View):
    def post(self, request):
        syllabus_ai_id = request.POST.get('syllabus_ai_id', None)
        reference = request.POST.get('reference', None)

        if not (syllabus_ai_id and reference):
            return JsonResponse({'error': 'Invalid data provided'}, status=400)

        try:
            syllabus_ai = Syllabus_AI.objects.get(id=syllabus_ai_id)
        except Syllabus_AI.DoesNotExist:
            return JsonResponse({'error': 'Syllabus_AI not found'}, status=404)

        new_reference = Sources.objects.create(
            syllabus_ai_id=syllabus_ai,
            reference=reference
        )

        response_data = {
            'id': new_reference.id,
            'reference': new_reference.reference,
            'syllabus_ai_id': syllabus_ai.id
        }

        return JsonResponse(response_data)

class UpdateReference(View):
    def get(self, request):
        reference_id = request.GET.get('reference_id', None)
        new_reference_name = request.GET.get('new_reference_name', None)

        reference = get_object_or_404(Sources, id=reference_id)
        reference.reference = new_reference_name
        reference.save()

        data = {
            'reference_id': reference.id,
            'reference': reference.reference
        }
        return JsonResponse(data)

class DeleteReference(View):
    def get(self, request):
        reference_id = request.GET.get('reference_id', None)

        if not reference_id:
            return JsonResponse({'error': 'Invalid reference_id provided'}, status=400)

        try:
            reference = Sources.objects.get(id=reference_id)
            syllabus_id = reference.syllabus_ai_id.id
            reference.delete()
            data = {
                'deleted': True,
                'syllabus_id': syllabus_id
            }
            return JsonResponse(data)
        except Sources.DoesNotExist:
            return JsonResponse({'error': 'Reference not found'}, status=404)

class RemoveSelectedReferences(View):
    def post(self, request):
        reference_ids = request.POST.getlist('reference_ids[]', [])

        # Perform the removal of selected references
        for reference_id in reference_ids:
            try:
                reference = Sources.objects.get(id=reference_id)
                reference.delete()
            except Sources.DoesNotExist:
                pass  # Handle if the reference doesn't exist

        return JsonResponse({'removed': True})

    def get(self, request):
        return JsonResponse({'error': 'Invalid request method'})

class RegenerateReferences(View):
    def post(self, request):
        response_data = {}

        syllabus = request.POST.get('syllabus_id')
        syllabus_ai = request.POST.get('syllabus_ai_id')

        print(f"Syllabus ID: {syllabus},Syllabus AI ID: {syllabus_ai}")

        try:
            syllabus = Syllabus.objects.get(id=syllabus)
            syllabus_ai = Syllabus_AI.objects.get(id=syllabus_ai)
            if syllabus.source_type == 'Specific' or '':
                syllabus.source_type = 'Auto'

            # Delete all child Specific_Source models
            Sources.objects.filter(syllabus_ai_id=syllabus_ai).delete()

            # Get the subject attribute from syllabus_ai_input model
            subject = syllabus.course_name

            # Use ask_openai to generate content
            prompt_message = f'Generate based on this language: {syllabus_ai.language}.Generate 5 popular and existing references on {subject}. Always Include the title of the references. Separate the sources using "|" or vertical bar. Do not explain, Do not comment, Do not add empty lines. Respond with a single line with this format. GENERATE ONLY 5 SOURCES. Do not include links and do not use any numbers to list down. ALWASYS INCLUDE THE YEAR OF THE REFERENCES. ENCLOSE THE YEAR WITH A PARENTHESIS. Include the authors inside the quotation marks. Do not put inside parentheses.FIND ONLY REFERENCES FROM YEAR 2016 AND ABOVE.Immediately list all the 5 sources or references with the vertical bar "|" for separating them. FOLLOW THIS FORMAT: "Title" by author (year)|"Title" by author (year)|"Title" by author (year)|"Title" by author (year)|"Title" by author (year) '
            new_raw_source_ai = ask_openai(prompt_message)

            # Store the new_raw_source_ai in raw_source_ai
            syllabus_ai.raw_source = new_raw_source_ai
            syllabus_ai.save()

            # Retrieve and split the content of raw_source_ai
            new_prompt_raw_source = syllabus_ai.raw_source
            references = new_prompt_raw_source.split('|')

            unique_reference = set()  # Track unique reference

            for reference_text in references:
                reference_text = reference_text.strip()
                if reference_text not in unique_reference:
                    unique_reference.add(reference_text)  # Add to set to track uniqueness

                    reference, created = Sources.objects.get_or_create(syllabus_ai_id=syllabus_ai, reference=reference_text)
                    if not created:
                        # Update the source if it already exists
                        reference.reference = reference_text
                        reference.save()


            response_data['success'] = True
            response_data['message'] = 'Regeneration successful'
            response_data['new_references'] = [ref.reference for ref in Sources.objects.filter(syllabus_ai_id=syllabus_ai)]

        except Syllabus_AI.DoesNotExist:
            response_data['success'] = False
            response_data['message'] = 'Syllabus not found'

        return JsonResponse(response_data)

class AddTopic(View):
    def post(self, request):
        syllabus_ai_id = request.POST.get('syllabus_ai_id', None)
        topic_name = request.POST.get('topic_name', None)

        if not (syllabus_ai_id and topic_name):
            return JsonResponse({'error': 'Invalid data provided'}, status=400)

        try:
            syllabus_ai = Syllabus_AI.objects.get(id=syllabus_ai_id)
        except Syllabus_AI.DoesNotExist:
            return JsonResponse({'error': 'Syllabus_AI not found'}, status=404)

        new_topic = Topic.objects.create(
            syllabus_ai_id=syllabus_ai,
            topic_name=topic_name
        )

        response_data = {
            'id': new_topic.id,
            'topic_name': new_topic.topic_name,
            'syllabus_ai_id': syllabus_ai.id
        }

        return JsonResponse(response_data)

class UpdateTopic(View):
    def get(self, request):
        topic_id = request.GET.get('topic_id', None)
        new_topic_name = request.GET.get('new_topic_name', None)

        topic = get_object_or_404(Topic, id=topic_id)
        topic.topic_name = new_topic_name
        topic.save()

        data = {
            'topic_id': topic.id,
            'topic_name': topic.topic_name
        }
        return JsonResponse(data)

class DeleteTopic(View):
    def get(self, request):
        topic_id = request.GET.get('topic_id', None)

        if not topic_id:
            return JsonResponse({'error': 'Invalid topic_id provided'}, status=400)

        try:
            topic = Topic.objects.get(id=topic_id)
            syllabus_id = topic.syllabus_ai_id.id
            topic.delete()
            data = {
                'deleted': True,
                'syllabus_id': syllabus_id
            }
            return JsonResponse(data)
        except Topic.DoesNotExist:
            return JsonResponse({'error': 'Topic not found'}, status=404)

class RemoveSelectedTopics(View):
    def post(self, request):
        topic_ids = request.POST.getlist('topic_ids[]', [])

        # Perform the removal of selected topics
        for topic_id in topic_ids:
            try:
                topic = Topic.objects.get(id=topic_id)
                topic.delete()
            except Topic.DoesNotExist:
                pass  # Handle if the topic doesn't exist

        return JsonResponse({'removed': True})

    def get(self, request):
        return JsonResponse({'error': 'Invalid request method'})

class RegenerateTopics(View):
    def post(self, request):
        response_data = {}

        syllabus_id = request.POST.get('syllabus_id')
        syllabus_ai_id = request.POST.get('syllabus_ai_id')

        print(f"Syllabus ID: {syllabus_id}, Syllabus AI ID: {syllabus_ai_id}")

        try:
            syllabus_id = Syllabus.objects.get(id=syllabus_id)
            syllabus_ai = Syllabus_AI.objects.get(id=syllabus_ai_id)

            # Clear the raw_topics content
            syllabus_ai.raw_topics = ''
            syllabus_ai.save()

            # Delete all child Topic models
            Topic.objects.filter(syllabus_ai_id=syllabus_ai).delete()

            # Retrieve all Specific Sources
            references = Sources.objects.filter(syllabus_ai_id=syllabus_ai)
            joined_references = ', '.join(reference.reference for reference in references)


            # Use ask_openai to generate content
            prompt_message = f'"Speak in this language:"{syllabus_ai.language}". And from these:{joined_references}". Get all the topics that can be gain from the references. Get Only 16 topics. Separate each topic by using a vertical bar "|". Do not explain, Do not comment, add labels, titles, Do not add empty lines. Respond with a single line. Use this template " Topic 1 | Topic 2 | ..."'
            new_raw_source_topics = ask_openai(prompt_message)

            # Store the new_raw_source_topics in raw_topics
            syllabus_ai.raw_source = joined_references
            syllabus_ai.raw_topics =  new_raw_source_topics
            syllabus_ai.save()
            # Retrieve and split the content of raw_topics
            new_prompt_raw_topic = syllabus_ai.raw_topics
            topics = re.split(r'[-*,A-Za-z0-9]\.\s*|\|', new_prompt_raw_topic)


            unique_topics = set()

            for topic_text in topics:
                topic_text = topic_text.strip()
                if topic_text not in unique_topics:
                    unique_topics.add(topic_text)
                    topic, created = Topic.objects.get_or_create(syllabus_ai_id=syllabus_ai, topic_name=topic_text)
                    if not created:
                        # Update the topic if it already exists
                        topic.topic_name = topic_text
                        topic.save()

            new_topics = [topic.topic_name for topic in Topic.objects.filter(syllabus_ai_id=syllabus_ai)]
            response_data['success'] = True
            response_data['message'] = 'Topic regeneration successful'
            response_data['new_topics'] = new_topics

        except Syllabus_AI.DoesNotExist:
            response_data['success'] = False
            response_data['message'] = 'Syllabus AI not found'

        return JsonResponse(response_data)

class AddCourseLearningOutcome(View):
    def post(self, request):
        syllabus_ai_id = request.POST.get('syllabus_ai_id', None)
        course_learning_outcome = request.POST.get('course_learning_outcome', None)

        if not (syllabus_ai_id and course_learning_outcome):
            return JsonResponse({'error': 'Invalid data provided'}, status=400)

        try:
            syllabus_ai = Syllabus_AI.objects.get(id=syllabus_ai_id)
        except Syllabus_AI.DoesNotExist:
            return JsonResponse({'error': 'Syllabus_AI not found'}, status=404)

        new_course_learning_outcome = Course_Learning_Outcome.objects.create(
            syllabus_ai_id=syllabus_ai,
            course_learning_outcome=course_learning_outcome
        )

        response_data = {
            'id': new_course_learning_outcome.id,
            'course_learning_outcome': new_course_learning_outcome.course_learning_outcome,
            'syllabus_ai_id': syllabus_ai.id
        }

        return JsonResponse(response_data)

class UpdateCourseLearningOutcome(View):
    def get(self, request):
        outcome_id = request.GET.get('outcome_id', None)
        new_outcome_text = request.GET.get('new_outcome_text', None)

        outcome = get_object_or_404(Course_Learning_Outcome, id=outcome_id)
        outcome.course_learning_outcome = new_outcome_text
        outcome.save()

        data = {
            'outcome_id': outcome.id,
            'course_learning_outcome': outcome.course_learning_outcome
        }
        return JsonResponse(data)

class DeleteCourseLearningOutcome(View):
    def get(self, request):
        outcome_id = request.GET.get('outcome_id', None)

        if not outcome_id:
            return JsonResponse({'error': 'Invalid outcome_id provided'}, status=400)

        try:
            outcome = Course_Learning_Outcome.objects.get(id=outcome_id)
            syllabus_ai_id = outcome.syllabus_ai_id.id
            outcome.delete()
            data = {
                'deleted': True,
                'syllabus_ai_id': syllabus_ai_id
            }
            return JsonResponse(data)
        except Course_Learning_Outcome.DoesNotExist:
            return JsonResponse({'error': 'Course Learning Outcome not found'}, status=404)

class RemoveSelectedCLOs(View):
    def post(self, request):
        clo_ids = request.POST.getlist('clo_ids[]', [])

        # Perform the removal of selected CLOs
        for clo_id in clo_ids:
            try:
                clo = Course_Learning_Outcome.objects.get(id=clo_id)
                clo.delete()
            except Course_Learning_Outcome.DoesNotExist:
                pass  # Handle if the CLO doesn't exist

        return JsonResponse({'removed': True})

    def get(self, request):
        return JsonResponse({'error': 'Invalid request method'})

class RegenerateCLO(View):
    def post(self, request):
        response_data = {}

        syllabus_id = request.POST.get('syllabus_id')
        syllabus_ai_id = request.POST.get('syllabus_ai_id')

        print(f"Syllabus ID: {syllabus_id}, Syllabus AI ID: {syllabus_ai_id}")

        try:
            syllabus_id = Syllabus.objects.get(id=syllabus_id)
            syllabus_ai = Syllabus_AI.objects.get(id=syllabus_ai_id)

            # Clear the raw_clo content
            syllabus_ai.raw_course_learning_outcomes = ''
            syllabus_ai.save()

            # Delete all child TCLO models
            Course_Learning_Outcome.objects.filter(syllabus_ai_id=syllabus_ai).delete()

            # Retrieve all topics
            topics = Topic.objects.filter(syllabus_ai_id=syllabus_ai)
            joined_topics = ', '.join(topic.topic_name for topic in topics)

            # Use ask_openai to generate content
            prompt_message = f'Speak in this language: {syllabus_ai.language},Based on the topics from: {joined_topics}. Generate at least 8 Course Learning Outcomes from the topics. Join topics if needed to accommodate all the topics. Do not use numbers immedialtely list all Course Learning Outcomes. Separate all Course Learning Outcomes by using a vertical bar "|". Do not explain, Do not comment, Do not add empty lines. Respond with a single line. Separate all Course Learning Outcomes by using a vertical bar "|"'
            new_raw_clo = ask_openai(prompt_message)

            # Store the new_raw_source_topics in raw_topics
            syllabus_ai.raw_topics = joined_topics
            syllabus_ai.raw_course_learning_outcomes = new_raw_clo
            syllabus_ai.save()

            # Retrieve and split the content of raw_topics
            new_prompt_raw_clo = syllabus_ai.raw_course_learning_outcomes
            clo_list = re.split(r'[-*A-Za-z0-9]\.\s*|\|', new_prompt_raw_clo)

            unique_clos = set()

            for clo_text in clo_list:
                clo_text = clo_text.strip()
                if clo_text not in unique_clos:
                    unique_clos.add(clo_text)
                    clo = Course_Learning_Outcome.objects.create(syllabus_ai_id=syllabus_ai, course_learning_outcome=clo_text)

            new_clos = [clo.course_learning_outcome for clo in Course_Learning_Outcome.objects.filter(syllabus_ai_id=syllabus_ai)]
            response_data['success'] = True
            response_data['message'] = 'CLO regeneration successful'
            response_data['new_clos'] = new_clos

        except Syllabus_AI.DoesNotExist:
            response_data['success'] = False
            response_data['message'] = 'Syllabus AI not found'

        return JsonResponse(response_data)

class SyllabusView2(TemplateView):
    template_name = 'user/ai_syllabus/show_info2.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        id = kwargs['id']  # Retrieve the 'id' parameter from the URL

        syllabus_ai = get_object_or_404(Syllabus_AI, id=id)  # HERE -----
        course_learning_outcomes = Course_Learning_Outcome.objects.filter(syllabus_ai_id=syllabus_ai)  # HERE -----
        course_outline = Course_Outline.objects.filter(syllabus_ai_id=syllabus_ai)
        course_rubric = Course_Rubric.objects.filter(syllabus_ai_id=syllabus_ai)
        course_rubric_item = Course_Rubric_Item.objects.filter(course_rubric_id__in=course_rubric)
        course_contents = Course_Content.objects.filter(course_outline_id__in=course_outline)
        dslos = Desired_Student_Learning_Outcome.objects.filter(course_outline_id__in=course_outline)
        obas = Outcome_Based_Activity.objects.filter(course_outline_id__in=course_outline)
        eoos = Evidence_of_Outcome.objects.filter(course_outline_id__in=course_outline)
        values = Values_Intended.objects.filter(course_outline_id__in=course_outline)
        # Move the retrieval of syllabus after other objects
        syllabus = None
        try:
            syllabus = Syllabus.objects.get(syllabus_ai_id=syllabus_ai)
        except Syllabus.DoesNotExist:
            pass

        if syllabus:
            print(syllabus.course_name)
            print(syllabus.id)
            print(syllabus.syllabus_name)
            print(syllabus_ai.id)
            print(syllabus_ai.first_time_processing)

        context['syllabus'] = syllabus
        context['syllabus_ai'] = syllabus_ai
        context['course_learning_outcomes'] = course_learning_outcomes
        context['course_outline'] = course_outline
        context['course_rubric'] = course_rubric
        context['course_rubric_item'] = course_rubric_item
        context['course_contents'] = course_contents
        context['dslos'] = dslos
        context['obas'] = obas
        context['eoos'] = eoos
        context['values'] = values

        return context

class ProcessAndRedirectView(View):
    def post(self, request, *args, **kwargs):
        syllabus_ai_id = kwargs.get('syllabus_ai_id')
        syllabus_id = request.POST.get('syllabusId')  # Get syllabusId from the POST data

        syllabus = Syllabus.objects.get(id=syllabus_id)

        # Update the first_time_processing attribute to 'No'
        syllabus_ai = get_object_or_404(Syllabus_AI, id=syllabus_ai_id)
        syllabus_ai.first_time_processing = Syllabus_AI.NO
        syllabus_ai.save()

        # Process course learning outcomes
        course_learning_outcomes = Course_Learning_Outcome.objects.filter(syllabus_ai_id=syllabus_ai_id).order_by('id')

        # Clean existing letters in course learning outcomes
        for clo in course_learning_outcomes:
            clo.course_learning_outcome = clo.course_learning_outcome.split('.', 1)[-1].strip()

        # Assign letters to course learning outcomes in ascending order
        lettered_clos = [f"{chr(65 + i)}. {clo.course_learning_outcome}" for i, clo in enumerate(course_learning_outcomes)]

        # Join course learning outcomes with "|"
        joined_clos = "|".join(lettered_clos)

        # Delete existing course learning outcomes
        Course_Learning_Outcome.objects.filter(syllabus_ai_id=syllabus_ai_id).delete()

        # Save joined course learning outcomes with letters in Syllabus_AI model
        syllabus_ai = get_object_or_404(Syllabus_AI, id=syllabus_ai_id)
        syllabus_ai.raw_course_learning_outcomes_ai_with_letters = joined_clos
        syllabus_ai.save()

        # Retrieve and split the content of raw_course_learning_outcomes_ai_with_letters
        new_prompt_raw_clo = syllabus_ai.raw_course_learning_outcomes_ai_with_letters
        clo_list = new_prompt_raw_clo.split('|')

        unique_clos = set()

        # Save the split course learning outcomes in Course_Learning_Outcome model
        for clo_text in clo_list:
            clo_text = clo_text.strip()
            if clo_text not in unique_clos:
                unique_clos.add(clo_text)
                clo = Course_Learning_Outcome.objects.create(syllabus_ai_id=syllabus_ai, course_learning_outcome=clo_text)

        # Retrieve all topics
        topics = Topic.objects.filter(syllabus_ai_id=syllabus_ai)
        joined_topics = ', '.join(topic.topic_name for topic in topics)

        prompt_clo = syllabus_ai.raw_course_learning_outcomes_ai_with_letters

        # Initialize course_outline outside the try block
        course_outline = None

        Course_Outline.objects.filter(syllabus_ai_id=syllabus_ai).delete()

        timeframe = syllabus.time_frame
        counter = 0
        while True:
            try:
                # prompt = f'Speak in this language: "{syllabus_ai.language}".Provide an exact 18 weeks weekly topics course outline for each of these topics "{joined_topics}" It should fit within time frame of EXACLTY 18 WEEKS. Week 9 and 18 should be midterm and final examination or laboratory base on topics provided and course outline. Do not exceed fit all the topics within the time frame one topic can be in a week or more than, feel free to suggest any additional areas of focus or related subjects that may enhance the depth and breadth of the content. Please include final examinations and should only be 1 week. Continue from week 1 until week 18. Adjust the hours according to the level of topic. Use this template ( time frame | Topic (No. of Hours/Topic) | Course Content | DESIRED STUDENT LEARNING OUTCOMES/COMPETENCIES At the end of each topic and semester, the students can: | OUTCOME-BASED (OBA) ACTIVITIES (Teaching & Learning Activities) | EVIDENCE OF OUTCOMES (Assessment of Learning Outcome) | COURSE LEARNING OUTCOMES | VALUES INTENDED ||). Each column should be separated by "|" and each weekly topic should be separated by "||". In COURSE LEARNING OUTCOMES column, if the topic is related to these course learning outcomes "{prompt_clo}" put the letter into course learning outline columns if one or more is related to each course outline row. For Values Intended, get the values that can be get from the topic. Do not put any label, do not put inside of quotations or parentheses. Do not explain, Do not comment and no footnote or other extra info and do not leave any columns blank. Provide it in a normal fonts and style and textual format, and in a single line without any break lines for all and provide and fit all topics within 18 weeks\' timeframe. DO NOT FORGET TO USE THE LANGUAGE: {syllabus_ai.language}.Sample output: Week 18 | Final Examination (5 hours) | ✓Review of Entire Course Content ✓Final Examination | ✓Demonstrate comprehensive understanding of the entire course content ✓Successfully complete the final examination | ✓Final Examination | ✓Final Examination Submission ✓Course Evaluation | A, B, C, D, E, F, G | ✓Problem-solving ✓Ethical reasoning || Week 3 and 4 |Software Project Documentation (5 hours) | ✓Documentation in Software Projects ✓Types of Documentation ✓Best Practices in Documentation | ✓Understand the importance of documentation in software projects ✓Identify and create different types of documentation ✓Apply best practices in documentation | ✓Class discussion ✓Audio-Visual Presentation ✓Hands-on Documentation Exercise | ✓Documentation Exercise Submission ✓Quiz | D, G | ✓Critical thinking ✓Values that was gain ||'
                prompt = f'Provide an exact 18 weeks weekly topics course outline in "{syllabus_ai.language} language response" for each of these topics "{joined_topics}" It should fit within time frame of EXACLTY 18 WEEKS. Week 9 and 18 should be midterm and final examination or laboratory base on topics provided and course outline. Do not exceed fit all the topics within the time frame one topic can be in a week or more than, feel free to suggest any additional areas of focus or related subjects that may enhance the depth and breadth of the content. Please include final examinations and should only be 1 week. Continue from week 1 until week 18. Adjust the hours according to the level of topic. Use this template ( time frame | Topic (No. of Hours/Topic) | Course Content | DESIRED STUDENT LEARNING OUTCOMES/COMPETENCIES At the end of each topic and semester, the students can: | OUTCOME-BASED (OBA) ACTIVITIES (Teaching & Learning Activities) | EVIDENCE OF OUTCOMES (Assessment of Learning Outcome) | COURSE LEARNING OUTCOMES | VALUES INTENDED ||). Each column should be separated by "|" and each weekly topic should be separated by "||". In COURSE LEARNING OUTCOMES column, if the topic is related to these course learning outcomes "{prompt_clo}" put the letter into course learning outline columns if one or more is related to each course outline row. For Values Intended, get the values that can be get from the topic .DO NOT FORGET TO USE THE LANGUAGE: {syllabus_ai.language} in responding and outputting informations. Do not put any label, do not put inside of quotations or parentheses. Do not explain, do not comment and no footnote or other extra info and do not leave any columns blank and fill all columns according to the reference and sample output you can use None instead of blank fields. Provide it in a normal fonts and style and textual format, and in a single line without any break lines for all and provide and fit all topics within 18 weeks\' timeframe. Sample output: Week 18 | Final Examination (5 hours) | ✓Review of Entire Course Content ✓Final Examination | ✓Demonstrate comprehensive understanding of the entire course content ✓Successfully complete the final examination | ✓Final Examination | ✓Final Examination Submission ✓Course Evaluation | A, B, C, D, E, F, G | ✓Problem-solving ✓Ethical reasoning || Week 3 and 4 |Software Project Documentation (5 hours) | ✓Documentation in Software Projects ✓Types of Documentation ✓Best Practices in Documentation | ✓Understand the importance of documentation in software projects ✓Identify and create different types of documentation ✓Apply best practices in documentation | ✓Class discussion ✓Audio-Visual Presentation ✓Hands-on Documentation Exercise | ✓Documentation Exercise Submission ✓Quiz | D, G | ✓Critical thinking ✓Values that was gain ||'
                syllabus_ai.raw_second_prompt = prompt
                syllabus_ai.save()
                response = ask_openai(prompt)
                syllabus_ai.raw_second_response = response
                syllabus_ai.save()

                syllabus_ai.raw_course_outline = syllabus_ai.raw_second_response
                syllabus_ai.save()

                reponse_cc = syllabus_ai.raw_course_outline

                # ----- PROCESS RAW OUTPUT -----
                raw_course_outlines = reponse_cc[:-3].strip().split('||')
                for raw_course_outline in raw_course_outlines:
                    # ----- SPLITTING FOR DIFFERENT COLUMNS OF COURSE OUTLINE -----
                    week, topic, raw_content, raw_dslo, raw_oba, raw_eoo, learning_outcome, raw_values = raw_course_outline.strip().split('|')

                    # ----- INSTANTIATION AND STORING OF NON LIST DATA -----
                    course_outline = Course_Outline(
                        syllabus_ai_id=syllabus_ai,
                        week=week, topic=topic,
                        course_learning_outcomes=learning_outcome
                        )
                    course_outline.save()

                    # ----- DATA PROCESS AND STORING TO TABLES OF LIST DATA -----
                    contents = raw_content[2:].strip().split('✓')
                    for content in contents:
                        course_content = Course_Content(course_outline_id=course_outline, course_content=content)
                        course_content.save()

                    dslos = raw_dslo[2:].strip().split('✓')
                    for dslo in dslos:
                        desired_student_learning_outcome = Desired_Student_Learning_Outcome(course_outline_id=course_outline, dslo=dslo)
                        desired_student_learning_outcome.save()

                    obas = raw_oba[2:].strip().split('✓')
                    for oba in obas:
                        outcome_based_activity = Outcome_Based_Activity(course_outline_id=course_outline, oba=oba)
                        outcome_based_activity.save()

                    eoos = raw_eoo[2:].strip().split('✓')
                    for eoo in eoos:
                        evidence_of_outcome = Evidence_of_Outcome(course_outline_id=course_outline, eoo=eoo)
                        evidence_of_outcome.save()

                    values = raw_values[2:].strip().split('✓')
                    for value in values:
                        values_intended = Values_Intended(course_outline_id=course_outline, values=value)
                        values_intended.save()

                break

            except ValueError as e:
                counter += 1
                syllabus_ai.raw_course_outline = f"Error: {e} {counter}"
                syllabus_ai.save()

                if course_outline:
                    course_outline.delete()

                continue

         # Get all Course_Outline instances created during the process

        # Redirect to the 'show_syllabus_second' URL
        redirect_url = reverse('show_syllabus_second', args=[syllabus_ai_id])
        return JsonResponse({'success': True, 'redirect_url': redirect_url})

class ProceeedAndRedirectView(View):
    def post(self, request, *args, **kwargs):
        syllabus_ai_id = kwargs.get('syllabus_ai_id')
        syllabus_id = request.POST.get('syllabusId')  # Get syllabusId from the POST data

        try:
            # Attempt to retrieve the Syllabus object
            syllabus = Syllabus.objects.get(id=syllabus_id)
        except Syllabus.DoesNotExist:
            # Handle the case where the Syllabus does not exist
            return JsonResponse({'success': False, 'message': 'Syllabus does not exist'})

        # Update the first_time_processing attribute to 'No'
        syllabus_ai = get_object_or_404(Syllabus_AI, id=syllabus_ai_id)
        syllabus_ai.first_time_processing = Syllabus_AI.NO
        syllabus_ai.save()

        # Process course learning outcomes
        course_learning_outcomes = Course_Learning_Outcome.objects.filter(syllabus_ai_id=syllabus_ai_id).order_by('id')

        with transaction.atomic():
            # Clean existing letters in course learning outcomes
            for clo in course_learning_outcomes:
                clo.course_learning_outcome = clo.course_learning_outcome.split('.', 1)[-1].strip()

            # Assign letters to course learning outcomes in ascending order
            lettered_clos = [f"{chr(65 + i)}. {clo.course_learning_outcome}" for i, clo in enumerate(course_learning_outcomes)]

            # Join course learning outcomes with "|"
            joined_clos = "|".join(lettered_clos)

            # Delete existing course learning outcomes
            Course_Learning_Outcome.objects.filter(syllabus_ai_id=syllabus_ai_id).delete()

            # Save joined course learning outcomes with letters in Syllabus_AI model
            syllabus_ai.raw_course_learning_outcomes_ai_with_letters = joined_clos
            syllabus_ai.save()

            # Retrieve and split the content of raw_course_learning_outcomes_ai_with_letters
            new_prompt_raw_clo = syllabus_ai.raw_course_learning_outcomes_ai_with_letters
            clo_list = new_prompt_raw_clo.split('|')

            unique_clos = set()

            # Save the split course learning outcomes in Course_Learning_Outcome model
            for clo_text in clo_list:
                clo_text = clo_text.strip()
                if clo_text not in unique_clos:
                    unique_clos.add(clo_text)
                    Course_Learning_Outcome.objects.create(syllabus_ai_id=syllabus_ai, course_learning_outcome=clo_text)

        # Redirect to the 'show_syllabus_second' URL
        redirect_url = reverse('show_syllabus_second', args=[syllabus_ai_id])
        return JsonResponse({'success': True, 'redirect_url': redirect_url})

class AddCourseOutlineView(View):
    def post(self, request):
        try:
            syllabus_ai_id = request.POST.get('syllabus_ai_id', None)
            topic = request.POST.get('topic')
            time_frame = request.POST.get('time_frame')
            clo = request.POST.get('clo')
            course_content_list = request.POST.getlist('course_content')
            dslo_list = request.POST.getlist('dslo')
            oba_list = request.POST.getlist('oba')
            eoo_list = request.POST.getlist('eoo')
            values_list = request.POST.getlist('values')

            if not (syllabus_ai_id and topic and time_frame and clo):
                return JsonResponse({'error': 'Invalid data provided'}, status=400)

            syllabus_ai = get_object_or_404(Syllabus_AI, id=syllabus_ai_id)

            print('syllabus_ai_id:', syllabus_ai_id)
            print('topic:', topic)
            print('time_frame:', time_frame)
            print('clo:', clo)
            # Create Course_Outline instance
            course_outline = Course_Outline.objects.create(
                syllabus_ai_id=syllabus_ai,
                week=time_frame,
                topic=topic,
                course_learning_outcomes=clo
            )
            print('course_content_list:', course_content_list)
            print('dslo_list:', dslo_list)
            print('oba_list:', oba_list)
            print('eoo_list:', eoo_list)
            print('values_list:', values_list)
            print('Received data:', request.POST)

            # Create Course_Content instances
            course_content_objects = []
            for content in course_content_list:
                course_content_obj = Course_Content.objects.create(course_outline_id=course_outline, course_content=content)
                course_content_objects.append({
                    'id': course_content_obj.id,
                    'content': course_content_obj.course_content,
                })

            # Create Desired_Student_Learning_Outcome instances
            dslo_objects = []
            for dslo in dslo_list:
                dslo_obj = Desired_Student_Learning_Outcome.objects.create(course_outline_id=course_outline, dslo=dslo)
                dslo_objects.append({
                    'id': dslo_obj.id,
                    'content': dslo_obj.dslo,
                })

            # Create Outcome_Based_Activity instances
            oba_objects = []
            for oba in oba_list:
                oba_obj = Outcome_Based_Activity.objects.create(course_outline_id=course_outline, oba=oba)
                oba_objects.append({
                    'id': oba_obj.id,
                    'content': oba_obj.oba,
                })

            # Create Evidence_of_Outcome instances
            eoo_objects = []
            for eoo in eoo_list:
                eoo_obj = Evidence_of_Outcome.objects.create(course_outline_id=course_outline, eoo=eoo)
                eoo_objects.append({
                    'id': eoo_obj.id,
                    'content': eoo_obj.eoo,
                })

            # Create Values_Intended instances
            values_objects = []
            for value in values_list:
                value_obj = Values_Intended.objects.create(course_outline_id=course_outline, values=value)
                values_objects.append({
                    'id': value_obj.id,
                    'content': value_obj.values,
                })

            response_data = {
                'success': True,
                'course_outline_id': course_outline.id,
            }

            response_data = {
                'success': True,
                'course_outline_id': course_outline.id,
                'topic': course_outline.topic,
                'week': course_outline.week,
                'course_learning_outcomes': course_outline.course_learning_outcomes,
                'course_content': course_content_objects,
                'dslo': dslo_objects,
                'oba': oba_objects,
                'eoo': eoo_objects,
                'values': values_objects,
            }

            return JsonResponse(response_data)

        except Exception as e:
            # Log the exception for further investigation
            print(e)
            return JsonResponse({'error': 'Internal server error'}, status=500)

class DeleteCourseOutline(View):
    def get(self, request):
        outline_id = request.GET.get('outline_id', None)

        if not outline_id:
            return JsonResponse({'error': 'Invalid outline_id provided'}, status=400)

        try:
            outline = Course_Outline.objects.get(id=outline_id)
            syllabus_ai_id = outline.syllabus_ai_id.id
            outline.delete()
            data = {
                'deleted': True,
                'syllabus_ai_id': syllabus_ai_id
            }
            return JsonResponse(data)
        except Course_Outline.DoesNotExist:
            return JsonResponse({'error': 'Course Outline not found'}, status=404)


class UpdateCourseOutline(View):
    def post(self, request):
        outline_id = request.POST.get('outline_id', None)
        new_topic = request.POST.get('new_topic', None)
        new_week = request.POST.get('new_week', None)
        new_clo = request.POST.get('new_clo', None)

        new_course_content_data = json.loads(request.POST.get('new-course_content', '[]'))
        deleted_course_content_data = json.loads(request.POST.get('deleted-course_content', '[]'))

        new_dslo_data = json.loads(request.POST.get('new-dslo', '[]'))
        deleted_dslo_data = json.loads(request.POST.get('deleted-dslo', '[]'))

        new_oba_data = json.loads(request.POST.get('new-oba', '[]'))
        deleted_oba_data = json.loads(request.POST.get('deleted-oba', '[]'))

        new_eoo_data = json.loads(request.POST.get('new-eoo', '[]'))
        deleted_eoo_data = json.loads(request.POST.get('deleted-eoo', '[]'))

        new_value_data = json.loads(request.POST.get('new-value', '[]'))
        deleted_value_data = json.loads(request.POST.get('deleted-value', '[]'))

        # Update Course_Outline details
        outline = get_object_or_404(Course_Outline, id=outline_id)
        outline.topic = new_topic
        outline.week = new_week
        outline.course_learning_outcomes = new_clo
        outline.save()
        print("outline - type(outline_id):", type(outline_id))


        # Update Course_Content details
        self.update_course_content(outline_id, new_course_content_data)

        # Delete Course_Content items
        self.delete_course_content(deleted_course_content_data)

        # Update dslo details
        self.update_dslo(outline_id, new_dslo_data)

        # Delete dslo items
        self.delete_dslo(deleted_dslo_data)

        # Update oba details
        self.update_oba(outline_id, new_oba_data)

        # Delete oba items
        self.delete_oba(deleted_oba_data)

        # Update eoo details
        self.update_eoo(outline_id, new_eoo_data)

        # Delete eoo items
        self.delete_eoo(deleted_eoo_data)

        # Update value details
        self.update_value(outline_id, new_value_data)

        # Delete value items
        self.delete_value(deleted_value_data)


        # Retrieve the updated outline with course content
        updated_outline = Course_Outline.objects.values('id', 'topic', 'week', 'course_learning_outcomes').get(id=outline_id)
        updated_outline['course_content'] = list(Course_Content.objects.filter(course_outline_id=outline_id).values('id', 'course_content'))
        updated_outline['dslo'] = list(Desired_Student_Learning_Outcome.objects.filter(course_outline_id=outline_id).values('id', 'dslo'))
        updated_outline['oba'] = list(Outcome_Based_Activity.objects.filter(course_outline_id=outline_id).values('id', 'oba'))
        updated_outline['eoo'] = list(Evidence_of_Outcome.objects.filter(course_outline_id=outline_id).values('id', 'eoo'))
        updated_outline['value'] = list(Values_Intended.objects.filter(course_outline_id=outline_id).values('id', 'values'))

        data = {
            'success': True,
            'message': 'Course outline updated successfully!',
            'outline_id': updated_outline['id'],
            'topic': updated_outline['topic'],
            'week': updated_outline['week'],
            'course_learning_outcomes': updated_outline['course_learning_outcomes'],
            'course_content': updated_outline['course_content'],
            'dslo': updated_outline['dslo'],
            'oba': updated_outline['oba'],
            'eoo': updated_outline['eoo'],
            'values': updated_outline['value'],
            # Add other fields if needed
        }
        return JsonResponse(data)

    def update_course_content(self, outline_id, new_values):
        # Extract the 'id' values and 'content' from each dictionary in new_values
        course_content_entries = [{'id': item.get('id'), 'content': item.get('content')} for item in new_values if 'id' in item]

        # Get existing course_content details for the outline
        existing_course_content = Course_Content.objects.filter(course_outline_id=outline_id)
        existing_ids_set = set(existing_course_content.values_list('id', flat=True))

        # Iterate over entries to update or create
        for entry in course_content_entries:
            entry_id = entry['id']
            content = entry['content']

            # Check if the entry_id exists in the current course content
            if entry_id in existing_ids_set:
                # Update existing entry
                Course_Content.objects.filter(id=entry_id).update(course_content=content)
            else:
                # Create new entry
                Course_Content.objects.create(course_outline_id=outline_id, course_content=content)

        # Identify items to delete
        items_to_delete = existing_ids_set - {entry['id'] for entry in course_content_entries}
        Course_Content.objects.filter(id__in=items_to_delete).delete()

    def delete_course_content(self, deleted_values):
        # Extract the 'id' values from each dictionary in deleted_values
        deleted_ids = [item.get('id') for item in deleted_values if 'id' in item]

        # Delete Course_Content items
        Course_Content.objects.filter(id__in=deleted_ids).delete()

    def update_dslo(self, outline_id, new_values):
        dslo_entries = [{'id': item.get('id'), 'content': item.get('content')} for item in new_values if 'id' in item]

        existing_dslo = Desired_Student_Learning_Outcome.objects.filter(course_outline_id=outline_id)
        existing_ids_set = set(existing_dslo.values_list('id', flat=True))

        for entry in dslo_entries:
            entry_id = entry['id']
            content = entry['content']

            if entry_id in existing_ids_set:
                Desired_Student_Learning_Outcome.objects.filter(id=entry_id).update(dslo=content)
            else:
                Desired_Student_Learning_Outcome.objects.create(course_outline_id=outline_id, dslo=content)

        items_to_delete = existing_ids_set - {entry['id'] for entry in dslo_entries}
        Desired_Student_Learning_Outcome.objects.filter(id__in=items_to_delete).delete()

    def delete_dslo(self, deleted_values):
        deleted_ids = [item.get('id') for item in deleted_values if 'id' in item]
        Desired_Student_Learning_Outcome.objects.filter(id__in=deleted_ids).delete()

    def update_oba(self, outline_id, new_values):
        oba_entries = [{'id': item.get('id'), 'content': item.get('content')} for item in new_values if 'id' in item]

        existing_oba = Outcome_Based_Activity.objects.filter(course_outline_id=outline_id)
        existing_ids_set = set(existing_oba.values_list('id', flat=True))

        for entry in oba_entries:
            entry_id = entry['id']
            content = entry['content']

            if entry_id in existing_ids_set:
                Outcome_Based_Activity.objects.filter(id=entry_id).update(oba=content)
            else:
                Outcome_Based_Activity.objects.create(course_outline_id=outline_id, oba=content)

        items_to_delete = existing_ids_set - {entry['id'] for entry in oba_entries}
        Outcome_Based_Activity.objects.filter(id__in=items_to_delete).delete()

    def delete_oba(self, deleted_values):
        deleted_ids = [item.get('id') for item in deleted_values if 'id' in item]
        Outcome_Based_Activity.objects.filter(id__in=deleted_ids).delete()
    def update_eoo(self, outline_id, new_values):
        eoo_entries = [{'id': item.get('id'), 'content': item.get('content')} for item in new_values if 'id' in item]

        existing_eoo = Evidence_of_Outcome.objects.filter(course_outline_id=outline_id)
        existing_ids_set = set(existing_eoo.values_list('id', flat=True))

        for entry in eoo_entries:
            entry_id = entry['id']
            content = entry['content']

            if entry_id in existing_ids_set:
                Evidence_of_Outcome.objects.filter(id=entry_id).update(eoo=content)
            else:
                Evidence_of_Outcome.objects.create(course_outline_id=outline_id, eoo=content)

        items_to_delete = existing_ids_set - {entry['id'] for entry in eoo_entries}
        Evidence_of_Outcome.objects.filter(id__in=items_to_delete).delete()

    def delete_eoo(self, deleted_values):
        deleted_ids = [item.get('id') for item in deleted_values if 'id' in item]
        Evidence_of_Outcome.objects.filter(id__in=deleted_ids).delete()
    def update_value(self, outline_id, new_values):
        value_entries = [{'id': item.get('id'), 'content': item.get('content')} for item in new_values if 'id' in item]

        existing_values = Values_Intended.objects.filter(course_outline_id=outline_id)
        existing_ids_set = set(existing_values.values_list('id', flat=True))

        for entry in value_entries:
            entry_id = entry['id']
            content = entry['content']

            if entry_id in existing_ids_set:
                Values_Intended.objects.filter(id=entry_id).update(values=content)
            else:
                Values_Intended.objects.create(course_outline_id=outline_id, values=content)

        items_to_delete = existing_ids_set - {entry['id'] for entry in value_entries}
        Values_Intended.objects.filter(id__in=items_to_delete).delete()

    def delete_value(self, deleted_values):
        deleted_ids = [item.get('id') for item in deleted_values if 'id' in item]
        Values_Intended.objects.filter(id__in=deleted_ids).delete()

class RegenerateCourseOutline(View):
    def post(self, request):
        # Initialize the response_data dictionary
        response_data = {}
        # Extract parameters from the request data
        syllabus_id = request.POST.get('syllabus')
        syllabus_ai_id = request.POST.get('syllabus_ai')
        course_outline_id = request.POST.get('outline_id')
        regen_option = request.POST.get('regen_option')  # Extract the regeneration option

        # Print the values for debugging
        print(f'Syllabus ID: {syllabus_id}, Syllabus AI ID: {syllabus_ai_id},Course Outine ID: {course_outline_id} ')
        print(regen_option)
        syllabus = Syllabus.objects.get(id=syllabus_id)
        syllabus_ai = Syllabus_AI.objects.get(id=syllabus_ai_id)
        course_outline = Course_Outline.objects.get(id=course_outline_id)

        if regen_option == 'topic':
            # Delete all child models
            Course_Content.objects.filter(course_outline_id=course_outline).delete()
            Desired_Student_Learning_Outcome.objects.filter(course_outline_id=course_outline).delete()
            Outcome_Based_Activity.objects.filter(course_outline_id=course_outline).delete()
            Evidence_of_Outcome.objects.filter(course_outline_id=course_outline).delete()
            Values_Intended.objects.filter(course_outline_id=course_outline).delete()

            course_outline.course_learning_outcomes = ''
            course_outline.save()

            prompt_0 = ask_openai('Based on this Course Learning Outcomes:'+ syllabus_ai.raw_course_learning_outcomes_ai_with_letters +'. Choose the letters that corresponds or similar or connected with the topic:'+ course_outline.topic +'. Example: A,C,D. Respond only with the letters with commas. Do not put period.')
            course_outline.course_learning_outcomes = prompt_0
            course_outline.save()

            # Use ask_openai to generate content
            prompt_1 = ask_openai('Speak in this language:'+ syllabus_ai.language +'Based on this Topic: '+ course_outline.topic  +'. And Based on this subject: '+ syllabus.course_name +'. Generate the Course Content for the topic. Split each item using a vertical bar "|". GIVE ONLY 5 ITEMS DO NOT EXCEED MORE THAN 5 ITEMS.USE VERTICAL BAR TO SPLIT. Do not use any other symbols to split ONLY VERTCAL BAR. Do not comment, do not use numbers, respond in one single line')

            # Split the text using the pipe symbol
            content_courses = prompt_1.split('|')

            # Assuming you have a Course_Content model
            for content_course in content_courses:
                # Trim whitespaces and create a new Course_Content instance
                course_content = Course_Content(course_outline_id=course_outline, course_content=content_course.strip())
                course_content.save()

            # Use ask_openai to generate content
            prompt_2 = ask_openai('Speak in this language:'+ syllabus_ai.language +'Based on this Topic: '+ course_outline.topic  +'. And Based on this subject: '+ syllabus.course_name +'. Generate the Desired Learning Outcomes for the topic.Do not use long sentences.   Split each item using a vertical bar "|". GIVE ONLY 5 ITEMS DO NOT EXCEED MORE THAN 5 ITEMS.USE VERTICAL BAR TO SPLIT. Do not use any other symbols to split ONLY VERTCAL BAR. Do not comment, do not use numbers, respond in one single line')

            # Split the text using the pipe symbol
            content_dslos = prompt_2.split('|')

            # Assuming you have a Course_Content model
            for content_dslo in content_dslos:
                # Trim whitespaces and create a new Course_Content instance
                dslo = Desired_Student_Learning_Outcome(course_outline_id=course_outline, dslo=content_dslo.strip())
                dslo.save()

            # Use ask_openai to generate content
            prompt_3 = ask_openai('Speak in this language:'+ syllabus_ai.language +'Based on this Topic: '+ course_outline.topic  +'. And Based on this subject: '+ syllabus.course_name +'. Generate the Outcome Based Activity based on the Course Content. Example of Outcome Based Activity: Class Discussion, Lab Activity:(Based this on the course Content), Audio Visual Presentation .Do not use long sentences.  Use only 5-6 words ONLY. Split each item using a vertical bar "|". Give at least 5 items.USE VERTICAL BAR TO SPLIT.Do not use any other symbols to split ONLY VERTCAL BAR. Do not comment, do not use numbers, respond in one single line')

            # Split the text using the pipe symbol
            content_obas = prompt_3.split('|')

            # Assuming you have a Course_Content model
            for content_oba in content_obas:
                # Trim whitespaces and create a new Course_Content instance
                oba = Outcome_Based_Activity(course_outline_id=course_outline, oba=content_oba.strip())
                oba.save()

            prompt_4 = ask_openai('Speak in this language:'+ syllabus_ai.language +'Based on this Topic: '+ course_outline.topic +'. And Based on this subject: '+ syllabus.course_name +'. Generate the Evidence of Outcome based on the Course Content. Example of Evidence of outcome: Quiz, Lab Activity Submision, Presentation.  Do not use long sentences. Use only 2-3 words ONLY. Split each item using a vertical bar "|". Give at least 5 items.USE VERTICAL BAR TO SPLIT.Do not use any other symbols to split ONLY VERTCAL BAR. Do not comment, do not use numbers, respond in one single line')

            # Split the text using the pipe symbol
            content_eoos = prompt_4.split('|')

            # Assuming you have a Course_Content model
            for content_eoo in content_eoos:
                # Trim whitespaces and create a new Course_Content instance
                eoo = Evidence_of_Outcome(course_outline_id=course_outline, eoo=content_eoo.strip())
                eoo.save()

            prompt_5 = ask_openai('Speak in this language:'+ syllabus_ai.language +'Based on this Topic: '+ course_outline.topic +'. And Based on this subject: '+ syllabus.course_name +'. Generate the Values integration or what values can be gain from the Topic.Do not use long sentences. Example of Values Integration: Critical Thinking, Analytical Reasoning. Use only 3-5 words ONLY. Split each item using a vertical bar "|". USE VERTICAL BAR TO SPLIT. Give at least 5 items.Do not use any other symbols to split ONLY VERTCAL BAR. Do not comment, do not use numbers, respond in one single line')

            # Split the text using the pipe symbol
            content_values = prompt_5.split('|')

            # Assuming you have a Course_Content model
            for content_value in content_values:
                # Trim whitespaces and create a new Course_Content instance
                value = Values_Intended(course_outline_id=course_outline, values=content_value.strip())
                value.save()

        elif regen_option == 'coursecontent':
            # Delete all child models
            Desired_Student_Learning_Outcome.objects.filter(course_outline_id=course_outline).delete()
            Outcome_Based_Activity.objects.filter(course_outline_id=course_outline).delete()
            Evidence_of_Outcome.objects.filter(course_outline_id=course_outline).delete()
            Values_Intended.objects.filter(course_outline_id=course_outline).delete()

            course_outline.course_learning_outcomes = ''
            course_outline.save()

            prompt_0 = ask_openai('Based on this Course Learning Outcomes:'+ syllabus_ai.raw_course_learning_outcomes_ai_with_letters +'. Choose the letters that corresponds or similar or connected with the topic:'+ course_outline.topic +'. Example: A,C,D. Respond only with the letters with commas. Do not put period.')
            course_outline.course_learning_outcomes = prompt_0
            course_outline.save()

            course_contents = Course_Content.objects.filter(course_outline_id=course_outline)
            joined_content = ', '.join(content.course_content for content in course_contents)


            # Use ask_openai to generate content
            prompt_2 = ask_openai('Speak in this language:'+ syllabus_ai.language +'Based on this Course Content: '+ joined_content +'. And Based on this subject: '+ syllabus.course_name +'. Generate the Desired Learning Outcomes for the topic.Do not use long sentences.   Split each item using a vertical bar "|". GIVE ONLY 5 ITEMS DO NOT EXCEED MORE THAN 5 ITEMS.USE VERTICAL BAR TO SPLIT. Do not use any other symbols to split ONLY VERTCAL BAR. Do not comment, do not use numbers, respond in one single line')

            # Split the text using the pipe symbol
            content_dslos = prompt_2.split('|')

            # Assuming you have a Course_Content model
            for content_dslo in content_dslos:
                # Trim whitespaces and create a new Course_Content instance
                dslo = Desired_Student_Learning_Outcome(course_outline_id=course_outline, dslo=content_dslo.strip())
                dslo.save()

            # Use ask_openai to generate content
            prompt_3 = ask_openai('Speak in this language:'+ syllabus_ai.language +'Based on this Course Content: '+ joined_content +'. And Based on this subject: '+ syllabus.course_name +'. Generate the Outcome Based Activity based on the Course Content. Example of Outcome Based Activity: Class Discussion, Lab Activity:(Based this on the course Content), Audio Visual Presentation .Do not use long sentences.  Use only 5-6 words ONLY. Split each item using a vertical bar "|". Give at least 5 items.USE VERTICAL BAR TO SPLIT.Do not use any other symbols to split ONLY VERTCAL BAR. Do not comment, do not use numbers, respond in one single line')

            # Split the text using the pipe symbol
            content_obas = prompt_3.split('|')

            # Assuming you have a Course_Content model
            for content_oba in content_obas:
                # Trim whitespaces and create a new Course_Content instance
                oba = Outcome_Based_Activity(course_outline_id=course_outline, oba=content_oba.strip())
                oba.save()

            prompt_4 = ask_openai('Speak in this language:'+ syllabus_ai.language +'Based on this Course Content: '+ joined_content +'. And Based on this subject: '+ syllabus.course_name +'. Generate the Evidence of Outcome based on the Course Content. Example of Evidence of outcome: Quiz, Lab Activity Submision, Presentation.  Do not use long sentences. Use only 2-3 words ONLY. Split each item using a vertical bar "|". Give at least 5 items.USE VERTICAL BAR TO SPLIT.Do not use any other symbols to split ONLY VERTCAL BAR. Do not comment, do not use numbers, respond in one single line')

            # Split the text using the pipe symbol
            content_eoos = prompt_4.split('|')

            # Assuming you have a Course_Content model
            for content_eoo in content_eoos:
                # Trim whitespaces and create a new Course_Content instance
                eoo = Evidence_of_Outcome(course_outline_id=course_outline, eoo=content_eoo.strip())
                eoo.save()

            prompt_5 = ask_openai('Speak in this language:'+ syllabus_ai.language +'Based on this Topic: '+ course_outline.topic +'. And Based on this subject: '+ syllabus.course_name +'. And Based on this Course Content:'+ joined_content +' Generate the Values integration or what values can be gain from the Topic and Course Content.Do not use long sentences. Example of Values Integration: Critical Thinking, Analytical Reasoning. Use only 3-5 words ONLY. Split each item using a vertical bar "|". USE VERTICAL BAR TO SPLIT. Give at least 5 items.Do not use any other symbols to split ONLY VERTCAL BAR. Do not comment, do not use numbers, respond in one single line')

            # Split the text using the pipe symbol
            content_values = prompt_5.split('|')

            # Assuming you have a Course_Content model
            for content_value in content_values:
                # Trim whitespaces and create a new Course_Content instance
                value = Values_Intended(course_outline_id=course_outline, values=content_value.strip())
                value.save()

        # Assuming your regeneration logic was successful
        response_data['success'] = True
        response_data['message'] = 'Regeneration was successful.'
        # Return a JsonResponse with the response_data
        return JsonResponse(response_data)


class AddCourseRubric(View):
    def post(self, request):
        syllabus_ai_id = request.POST.get('syllabus_ai_id', None)
        rubric_title = request.POST.get('rubric_title', None)

        if not (syllabus_ai_id and rubric_title):
            return JsonResponse({'error': 'Invalid data provided'}, status=400)

        try:
            syllabus_ai = Syllabus_AI.objects.get(id=syllabus_ai_id)
        except Syllabus_AI.DoesNotExist:
            return JsonResponse({'error': 'Syllabus_AI not found'}, status=404)

        new_rubric = Course_Rubric.objects.create(
            syllabus_ai_id=syllabus_ai,
            title=rubric_title
        )

        response_data = {
            'id': new_rubric.id,
            'title': new_rubric.title,
            'syllabus_ai_id': syllabus_ai.id
        }

        return JsonResponse(response_data)

class DeleteCourseRubric(View):
    def get(self, request):
        rubric_id = request.GET.get('rubric_id', None)

        if not rubric_id:
            return JsonResponse({'error': 'Invalid rubric_id provided'}, status=400)

        try:
            rubric = Course_Rubric.objects.get(id=rubric_id)
            rubric.delete()
            data = {
                'deleted': True,
                'rubric_id': rubric_id
            }
            return JsonResponse(data)
        except Course_Rubric.DoesNotExist:
            return JsonResponse({'error': 'Course Rubric not found'}, status=404)

class UpdateCourseRubric(View):
    def get(self, request):
        rubric_id = request.GET.get('rubric_id', None)
        new_rubric_title = request.GET.get('new_rubric_title', None)

        rubric = get_object_or_404(Course_Rubric, id=rubric_id)
        rubric.title = new_rubric_title
        rubric.save()

        data = {
            'rubric_id': rubric.id,
            'rubric_title': rubric.title
        }
        return JsonResponse(data)

class RegenerateCourseRubricView(View):
    def post(self, request):
        # Initialize the response_data dictionary
        response_data = {}
        # Extract parameters from the request data
        syllabus_id = request.POST.get('syllabus')
        syllabus_ai_id = request.POST.get('syllabus_ai')
        rubric_id = request.POST.get('rubric_id')

        # Print the values for debugging
        print(f'Syllabus ID: {syllabus_id}, Syllabus AI ID: {syllabus_ai_id},Rubric ID: {rubric_id} ')
        # Your regeneration logic here
        try:
            syllabus = Syllabus.objects.get(id=syllabus_id)
            syllabus_ai = Syllabus_AI.objects.get(id=syllabus_ai_id)
            rubric = Course_Rubric.objects.get(id=rubric_id)

            # Clear the content
            rubric.raw_source_course_rubric_ai = ''
            rubric.save()

            # Delete all child models
            Course_Rubric_Item.objects.filter(course_rubric_id=rubric).delete()

            # Retrieve all topics
            topics = Topic.objects.filter(syllabus_ai_id=syllabus_ai)
            joined_topics = ', '.join(topic.topic_name for topic in topics)

            # Use ask_openai to generate content
            prompt_message = f'Speak in this language: "{syllabus_ai.language}".Generate a table for rubrics'+ rubric.title +' for the subject:'+ syllabus.course_name +' and Based on these Topics: '+ joined_topics +'.First Column is the Criteria Name:(Example: Organization(15%)). Second Column for beginner (Example:Very hard to find information.6pts.) Third Column: Capable (Example: Information difficult to locate.9pts) Fourth Column for Accomplished (Example:Can find information with slight effort. 12pts) Fifth Column for Expert (Example: All information is easy to find and important points stand out.15pts) Do only 5 Criteria Based on the topics and subject. Do not comment, Do not add anything. Do not add any headers. Do not Use Parenthesis. Use the DOUBLE VERITCAL LINE "||" to proceed to the next criteria.Follow this given format: (Criteria✓Beginner✓Capable✓Accomplished✓Expert||Criteria✓Beginner✓Capable✓Accomplished✓Expert||Criteria✓Beginner✓Capable✓Accomplished✓Expert||Criteria✓Beginner✓Capable✓Accomplished✓Expert) Example of Format: Organization (20%)✓The information appears to be disorganized.8pts✓Information is organized, but paragraphs are not wellconstructed. 12pts✓ Information is organized with well-constructed paragraphs.16pts✓Information is very organized with well-constructed paragraphs and subheadings.20pts||Amount of Information (30%)✓ One or more topics were not addressed.12pts✓All topics are addressed, and most questions are answered with 1 sentence about each.18pts✓All topics are addressed and most questions answered with at least 2 sentences about each.24pts✓All topics are addressed and all questions answered with at least 2 sentences about each.30pts.Do not forget the double vertical line to separate the criterias , the percentage of each criteria must all sum up into 100 percent and the points of each items. DO NOT PUT A DOUBLE VERICAL LINE IN THE END. DO NOT FORGET THE PERCENTAGE OF EACH CRITERIA. DO NOT FORGET TO SPEAK IN THIS LANGUAGE:'+ syllabus_ai.language +'.DO NOT FORGET TO PUT DOUBLE VERTICAL "||" TO SEPARATE EACH CRITERIA. ALWAYS PUT DOUBLE VERTICAL LINE WHEN PROCEEDING TO THE NEXT CRITERIA'
            new_raw_cr = ask_openai(prompt_message)

            rubric.raw_source_course_rubric_ai = new_raw_cr
            rubric.save()
            # Split the text into criteria based on double vertical bars (||)
            criteria_list = new_raw_cr.split("||")

            # Iterate through each criteria and create Course_Rubric_Item objects
            for criteria_text in criteria_list:
                # Split each criteria into its components
                components = criteria_text.split('✓')

                # Extract components (assuming each criteria has the same structure)
                criteria_name = components[0].strip()
                beginner = components[1].strip()
                capable = components[2].strip()
                accomplished = components[3].strip()
                expert = components[4].strip()

                # Assuming you have a Course_Rubric object to associate with (replace with the actual rubric object)
                course_rubric = Course_Rubric.objects.get(id=rubric_id)

                # Create a Course_Rubric_Item object
                rubric_item = Course_Rubric_Item.objects.create(
                    course_rubric_id=course_rubric,
                    criteria=criteria_name,
                    beginner=beginner,
                    capable=capable,
                    accomplished=accomplished,
                    expert=expert
                )

                # Save the object
                rubric_item.save()

            # Store the new_raw_source_topics in raw_topics
            rubric.raw_source_course_rubric_ai= new_raw_cr
            rubric.save()


            # Assuming your regeneration logic was successful
            response_data['success'] = True
            response_data['message'] = 'Regeneration was successful.'
            # Assuming new_clos is the correct data to be sent
            response_data['new_raw_cr'] = new_raw_cr

        except Course_Rubric.DoesNotExist:
            response_data['success'] = False
            response_data['message'] = 'Course Rubric not found'

        # Return a JsonResponse with the response_data
        return JsonResponse(response_data)

class AddCourseRubricItem(View):
    def post(self, request, *args, **kwargs):
        # Assuming the form data is submitted via POST request
        rubric_id = request.POST.get('course_rubric_id')
        criteria = request.POST.get('criteria')
        beginner = request.POST.get('beginner')
        capable = request.POST.get('capable')
        accomplished = request.POST.get('accomplished')
        expert = request.POST.get('expert')

        # Assuming you have proper validation and error handling here

        # Retrieve the Course_Rubric instance based on the ID
        course_rubric = get_object_or_404(Course_Rubric, id=rubric_id)

        # Create a new Course_Rubric_Item instance
        course_rubric_item = Course_Rubric_Item(
            course_rubric_id=course_rubric,
            criteria=criteria,
            beginner=beginner,
            capable=capable,
            accomplished=accomplished,
            expert=expert
        )

        # Save the instance to the database
        course_rubric_item.save()

        # You can customize the data you want to return in the JSON response
        data = {
            'success': True,
            'message': 'Course Rubric Item added successfully',
            'course_rubric_id': course_rubric.id,  # Include course_rubric_id in the response
            'course_rubric_item_id': course_rubric_item.id,
            'criteria': course_rubric_item.criteria,
            'beginner': course_rubric_item.beginner,
            'capable': course_rubric_item.capable,
            'accomplished': course_rubric_item.accomplished,
            'expert': course_rubric_item.expert,
        }
        print("Data sent to client:", data)

        return JsonResponse(data)

class DeleteCourseRubricItem(View):
    def post(self, request, *args, **kwargs):
        rubric_item_id = request.POST.get('rubric_item_id')

        # Assuming you have proper validation and error handling here

        # Try to delete the rubric item
        try:
            rubric_item = Course_Rubric_Item.objects.get(id=rubric_item_id)
            rubric_item.delete()
            success = True
        except Course_Rubric_Item.DoesNotExist:
            success = False

        # You can customize the data you want to return in the JSON response
        data = {
            'success': success,
            'message': 'Course Rubric Item deleted successfully',
        }

        return JsonResponse(data)

class EditCourseRubricItem(View):
    def post(self, request, *args, **kwargs):
        # Assuming the form data is submitted via POST request
        rubric_item_id = request.POST.get('editCourseRubricItemId')
        criteria = request.POST.get('editCriteria')
        beginner = request.POST.get('editBeginner')
        capable = request.POST.get('editCapable')
        accomplished = request.POST.get('editAccomplished')
        expert = request.POST.get('editExpert')

        # Assuming you have proper validation and error handling here

        # Retrieve the Course_Rubric_Item instance based on the ID
        course_rubric_item = get_object_or_404(Course_Rubric_Item, id=rubric_item_id)

        # Update the Course_Rubric_Item instance
        course_rubric_item.criteria = criteria
        course_rubric_item.beginner = beginner
        course_rubric_item.capable = capable
        course_rubric_item.accomplished = accomplished
        course_rubric_item.expert = expert

        # Save the changes to the database
        course_rubric_item.save()

        # You can customize the data you want to return in the JSON response
        data = {
            'success': True,
            'message': 'Course Rubric Item updated successfully',
            'course_rubric_item_id': course_rubric_item.id,
            'criteria': course_rubric_item.criteria,
            'beginner': course_rubric_item.beginner,
            'capable': course_rubric_item.capable,
            'accomplished': course_rubric_item.accomplished,
            'expert': course_rubric_item.expert,
        }

        return JsonResponse(data)

class AddNewCourseContent(View):
    def post(self, request):
        course_outline_id = request.POST.get('course_outline_id', None)
        course_content = request.POST.get('course_content', None)

        if not (course_outline_id and course_content):
            return JsonResponse({'error': 'Invalid data provided'}, status=400)

        try:
            course_outline = Course_Outline.objects.get(id=course_outline_id)
        except Course_Outline.DoesNotExist:
            return JsonResponse({'error': 'Course_Outline not found'}, status=404)

        new_course_content = Course_Content.objects.create(
            course_outline_id=course_outline,
            course_content=course_content
        )

        response_data = {
            'id': new_course_content.id,
            'course_content': new_course_content.course_content,
            'course_outline_id': course_outline.id
        }

        return JsonResponse(response_data)

class AddNewDSLO(View):
    def post(self, request):
        course_outline_id = request.POST.get('course_outline_id', None)
        dslo_content = request.POST.get('dslo_content', None)

        if not (course_outline_id and dslo_content):
            return JsonResponse({'error': 'Invalid data provided'}, status=400)

        try:
            course_outline = Course_Outline.objects.get(id=course_outline_id)
        except Course_Outline.DoesNotExist:
            return JsonResponse({'error': 'Course_Outline not found'}, status=404)

        new_dslo = Desired_Student_Learning_Outcome.objects.create(
            course_outline_id=course_outline,
            dslo=dslo_content
        )

        response_data = {
            'id': new_dslo.id,
            'dslo_content': new_dslo.dslo,
            'course_outline_id': course_outline.id
        }

        return JsonResponse(response_data)

class AddNewOBA(View):
    def post(self, request):
        course_outline_id = request.POST.get('course_outline_id', None)
        oba_content = request.POST.get('oba_content', None)

        if not (course_outline_id and oba_content):
            return JsonResponse({'error': 'Invalid data provided'}, status=400)

        try:
            course_outline = Course_Outline.objects.get(id=course_outline_id)
        except Course_Outline.DoesNotExist:
            return JsonResponse({'error': 'Course_Outline not found'}, status=404)

        new_oba = Outcome_Based_Activity.objects.create(
            course_outline_id=course_outline,
            oba=oba_content
        )

        response_data = {
            'id': new_oba.id,
            'oba_content': new_oba.oba,
            'course_outline_id': course_outline.id
        }

        return JsonResponse(response_data)

class AddNewEOO(View):
    def post(self, request):
        course_outline_id = request.POST.get('course_outline_id', None)
        eoo_content = request.POST.get('eoo_content', None)

        if not (course_outline_id and eoo_content):
            return JsonResponse({'error': 'Invalid data provided'}, status=400)

        try:
            course_outline = Course_Outline.objects.get(id=course_outline_id)
        except Course_Outline.DoesNotExist:
            return JsonResponse({'error': 'Course_Outline not found'}, status=404)

        new_eoo = Evidence_of_Outcome.objects.create(
            course_outline_id=course_outline,
            eoo=eoo_content
        )

        response_data = {
            'id': new_eoo.id,
            'eoo_content': new_eoo.eoo,
            'course_outline_id': course_outline.id
        }

        return JsonResponse(response_data)

class AddNewValues(View):
    def post(self, request):
        course_outline_id = request.POST.get('course_outline_id', None)
        values_content = request.POST.get('values_content', None)

        if not (course_outline_id and values_content):
            return JsonResponse({'error': 'Invalid data provided'}, status=400)

        try:
            course_outline = Course_Outline.objects.get(id=course_outline_id)
        except Course_Outline.DoesNotExist:
            return JsonResponse({'error': 'Course_Outline not found'}, status=404)

        new_values = Values_Intended.objects.create(
            course_outline_id=course_outline,
            values=values_content
        )

        response_data = {
            'id': new_values.id,
            'values_content': new_values.values,
            'course_outline_id': course_outline.id
        }

        return JsonResponse(response_data)

@login_required
def pdf(request, id):
    # ---------- SYLLABUS ----------
    syllabus = get_object_or_404(Syllabus, user_id=request.user, id=id)
    preriquisite = Preriquisite.objects.filter(syllabus_id=syllabus)
    course_requirements = Course_Requirements.objects.filter(syllabus_id=syllabus)
    prepared = Prepared.objects.filter(syllabus_id=syllabus)

    # ---------- SYLLABUS TEMPLATE ----------
    syllabus_template = get_object_or_404(Syllabus_Template, user_id=request.user, id=syllabus.syllabus_template_id.id)
    wmsu_logo = Logo.objects.get(syllabus_template_id=syllabus_template, name='wmsu_logo')
    course_logo = Logo.objects.get(syllabus_template_id=syllabus_template, name='course_logo')
    iso_logo = Logo.objects.get(syllabus_template_id=syllabus_template, name='iso_logo')
    vision = Vision.objects.get(syllabus_template_id=syllabus_template)
    vision_itemizes = Vision_Itemize.objects.filter(syllabus_template_id=syllabus_template)
    mission = Mission.objects.get(syllabus_template_id=syllabus_template)
    mission_itemizes = Mission_Itemize.objects.filter(syllabus_template_id=syllabus_template)
    goal = Goal.objects.get(syllabus_template_id=syllabus_template)
    goal_itemizes = Goal_Itemize.objects.filter(syllabus_template_id=syllabus_template)
    course_outcome = Course_Outcome.objects.filter(syllabus_template_id=syllabus_template)

    # ---------- SYLLABUS AI ----------
    syllabus_ai = get_object_or_404(Syllabus_AI, user_id=request.user, id=syllabus.syllabus_ai_id.id)
    sources = Sources.objects.filter(syllabus_ai_id=syllabus_ai)
    learning_outcome = Course_Learning_Outcome.objects.filter(syllabus_ai_id=syllabus_ai)
    course_outline = Course_Outline.objects.filter(syllabus_ai_id=syllabus_ai)
    course_rubric = Course_Rubric.objects.filter(syllabus_ai_id=syllabus_ai)

    # ---------- GRADING SYSTEM ----------
    if syllabus.grading_system_option == "create-new":  # if user created a new one from syllabus
        grading_system = Syllabus_Grading_System.objects.get(syllabus_id=syllabus)
        midterm = Syllabus_Term_Grade.objects.get(grading_system_id=grading_system, term_name='midterm')
        midterm_lecture = Syllabus_Term_Description.objects.filter(term_grade_id=midterm, lecture_percentage__isnull=False)
        midterm_laboratory = Syllabus_Term_Description.objects.filter(term_grade_id=midterm, laboratory_percentage__isnull=False)
        finalterm = Syllabus_Term_Grade.objects.get(grading_system_id=grading_system, term_name='finalterm')
        finalterm_lecture = Syllabus_Term_Description.objects.filter(term_grade_id=finalterm, lecture_percentage__isnull=False)
        finalterm_laboratory = Syllabus_Term_Description.objects.filter(term_grade_id=finalterm, laboratory_percentage__isnull=False)
        percentage_grade_range = Syllabus_Percentage_Grade_Range.objects.filter(grading_system_id=grading_system)

    else:  # if user picked the grading system from template
        grading_system = Grading_System.objects.get(syllabus_template_id=syllabus_template)
        midterm = Term_Grade.objects.get(grading_system_id=grading_system, term_name='midterm')
        midterm_lecture = Term_Description.objects.filter(term_grade_id=midterm, lecture_percentage__isnull=False)
        midterm_laboratory = Term_Description.objects.filter(term_grade_id=midterm, laboratory_percentage__isnull=False)
        finalterm = Term_Grade.objects.get(grading_system_id=grading_system, term_name='finalterm')
        finalterm_lecture = Term_Description.objects.filter(term_grade_id=finalterm, lecture_percentage__isnull=False)
        finalterm_laboratory = Term_Description.objects.filter(term_grade_id=finalterm, laboratory_percentage__isnull=False)
        percentage_grade_range = Percentage_Grade_Range.objects.filter(grading_system_id=grading_system)

    total_term_percentage = midterm.term_percentage + finalterm.term_percentage

    wmsu_logo = str(settings.PDF_LOGO) + '/' + wmsu_logo.img_name
    course_logo = str(settings.PDF_LOGO) + '/' + course_logo.img_name
    iso_logo = str(settings.PDF_LOGO) + '/' + iso_logo.img_name

    template = loader.get_template('PDF_template/template.html') # Load HTML template
    html_string = template.render({
        # ----- SYLLABUS -----
        'syllabus': syllabus,
        'preriquisites': preriquisite,
        'course_requirements': course_requirements,
        'prepares': prepared,

        # ----- SYLLABUS TEMPLATE -----
        'syllabus_template': syllabus_template,
        'wmsu_logo': wmsu_logo,
        'course_logo': course_logo,
        'iso_logo': iso_logo,
        'vision': vision,
        'vision_itemizes': vision_itemizes,
        'mission': mission,
        'mission_itemizes': mission_itemizes,
        'goal': goal,
        'goal_itemizes': goal_itemizes,
        'course_outcomes': course_outcome,

        # ----- SYLLABUS AI -----
        'syllabus_ai': syllabus_ai,
        'sources': sources,
        'learning_outcomes': learning_outcome,
        'course_outlines': course_outline,
        'course_rubrics': course_rubric,

        # ----- GRADING SYSTEM -----
        'midterm': midterm,
        'midterm_lectures': midterm_lecture,
        'midterm_laboratories': midterm_laboratory,
        'finalterm': finalterm,
        'finalterm_lectures': finalterm_lecture,
        'finalterm_laboratories': finalterm_laboratory,
        'total_term_percentage': total_term_percentage,
        'percentage_grade_ranges': percentage_grade_range,
    }) # Render the template

    # Generate the PDF using WeasyPrint
    # pdf = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()
    base_url = settings.PDF_LOGO
    pdf = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf(presentational_hints=True)
    # pdf = html.write_pdf(stylesheets=[CSS(settings.STATIC_ROOT +  '/css/detail_pdf_gen.css')], presentational_hints=True);

    # Create an HttpResponse with the PDF content
    response = HttpResponse(pdf, content_type='application/pdf')
    # Display in the browser
    response['Content-Disposition'] = 'inline; filename=Syllabus' + str(datetime.datetime.now()) + '.pdf'

    return response

# ---------- global reusable functions  ----------
def add_grading_system(term_id, term, type, request, isSyllabus):
    grade = request.POST[term+'-'+type+'-grade']
    if not grade: grade = 0 # if empty

    description_values = request.POST.getlist(term+'-'+type+'-description')
    percentage_values = request.POST.getlist(term+'-'+type+'-percentage')

    # store both values in term_description table
    for description, percentage in zip(description_values, percentage_values):
        if not percentage: percentage = 0 # if percentage is empty

        if isSyllabus: # Check if for syllabus or for template
            term_description = Syllabus_Term_Description(term_grade_id = term_id)

        else:
            term_description = Term_Description(term_grade_id = term_id)

        term_description.term_description = description
        term_description.percentage = percentage

        if type == 'lecture':
            term_description.lecture_percentage = grade

        elif type == 'laboratory':
            term_description.laboratory_percentage = grade

        term_description.save()

    return True

# --------------- GLOBAL DATA ---------------
# ----- for like navbars or others that is used as extends or includes -----
def global_data(request):
    context = {}

    if request.user.is_authenticated:
        # If the user is authenticated, use their account for the syllabus input
        account = request.user

        # Fetch data from the database
        syllabus = Syllabus.objects.filter(user_id=account)
        syllabus_template = Syllabus_Template.objects.filter(user_id=account)

        context['syllabuses'] = syllabus
        context['syllabus_templates'] = syllabus_template
    else:
        # If the user is not authenticated, set a flag in the context
        context['redirect_to_login'] = True

    return context