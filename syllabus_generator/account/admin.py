from django.contrib import admin
from account.models import Account, CustomUser
from account.forms import CustomUserCreationForm, CustomUserChangeForm
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
# Register your models here.

class AccountInLine(admin.StackedInline):
    model = Account
    can_delete = False
    verbose_name_plural = 'Accounts'

class CustomizedUserAdmin(admin.ModelAdmin):  # Update this line
    inlines = (AccountInLine, )

class CustomUserAdmin(admin.ModelAdmin):  # Update this line
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ["username", "email", "is_staff", "is_superuser"]

# Register the admin classes
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Account)

# Register the default User model
admin.site.register(User)  # Add this line to keep the default User model registered