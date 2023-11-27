from django import forms
from PIL import Image
from django.contrib.auth.forms import PasswordChangeForm

class LogoUploadForm(forms.Form):
    course_logo = forms.FileField(label='Course Logo', required=False)
    wmsu_logo = forms.FileField(label='WMSU Logo', required=False)
    iso_logo = forms.FileField(label='ISO Logo', required=False)

    def clean(self):
        cleaned_data = super().clean()

        for field_name, uploaded_file in self.files.items():
            try:
                # Attempt to open the image using Pillow
                Image.open(uploaded_file)
            except (IOError, ValueError):
                self.add_error(field_name, 'Invalid logo, please try again.')

        return cleaned_data
    
class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, user, *args, **kwargs):
        super(CustomPasswordChangeForm, self).__init__(user, *args, **kwargs)
        del self.fields['old_password']

class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(label='WMSU Email', widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'WMSU E-mail'}))