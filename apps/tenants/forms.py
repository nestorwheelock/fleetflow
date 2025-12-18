"""
Authentication and user management forms for FleetFlow.

All forms use email as the primary identifier (not username).
"""
from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.forms import (
    AuthenticationForm,
    UserCreationForm,
    PasswordResetForm,
    SetPasswordForm,
)
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class EmailAuthenticationForm(AuthenticationForm):
    """
    Authentication form that uses email instead of username.

    Provides case-insensitive email authentication with clear error messages.
    """
    username = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(attrs={
            'autofocus': True,
            'class': 'form-input',
            'placeholder': 'you@example.com',
            'autocomplete': 'email',
        })
    )
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': '••••••••',
            'autocomplete': 'current-password',
        }),
    )

    error_messages = {
        'invalid_login': _(
            "Invalid email or password. Please check your credentials and try again."
        ),
        'inactive': _("This account is inactive. Please contact support."),
    }

    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if email is not None and password:
            # Normalize email to lowercase for case-insensitive matching
            email = email.lower()
            self.user_cache = authenticate(
                self.request, email=email, password=password
            )
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


class EmailUserCreationForm(UserCreationForm):
    """
    User creation form that uses email as the primary identifier.

    Used for both customer registration and staff user creation.
    """
    email = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'you@example.com',
            'autocomplete': 'email',
        }),
        help_text=_("Enter a valid email address. This will be your login.")
    )
    first_name = forms.CharField(
        label=_("First Name"),
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'John',
            'autocomplete': 'given-name',
        })
    )
    last_name = forms.CharField(
        label=_("Last Name"),
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Doe',
            'autocomplete': 'family-name',
        })
    )
    phone = forms.CharField(
        label=_("Phone Number"),
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': '(555) 123-4567',
            'autocomplete': 'tel',
        })
    )
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': '••••••••',
            'autocomplete': 'new-password',
        }),
    )
    password2 = forms.CharField(
        label=_("Confirm Password"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': '••••••••',
            'autocomplete': 'new-password',
        }),
        strip=False,
    )

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'phone', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower()
            if User.objects.filter(email__iexact=email).exists():
                raise ValidationError(
                    _("A user with this email already exists."),
                    code='email_exists',
                )
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email'].lower()
        if commit:
            user.save()
        return user


class CustomerRegistrationForm(EmailUserCreationForm):
    """
    Registration form specifically for rental customers.

    Sets is_customer=True and handles tenant context.
    """

    class Meta(EmailUserCreationForm.Meta):
        fields = ('email', 'first_name', 'last_name', 'phone', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_customer = True
        if commit:
            user.save()
        return user


class StaffInviteForm(forms.Form):
    """
    Form for inviting staff members to a tenant.

    If the email exists, adds them to tenant. If not, creates new user and adds.
    """
    email = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'staff@example.com',
        })
    )
    first_name = forms.CharField(
        label=_("First Name"),
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'First name',
        })
    )
    last_name = forms.CharField(
        label=_("Last Name"),
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Last name',
        })
    )
    role = forms.ChoiceField(
        label=_("Role"),
        choices=[
            ('staff', 'Staff'),
            ('manager', 'Manager'),
        ],
        widget=forms.Select(attrs={'class': 'form-input'})
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            return email.lower()
        return email


class EmailPasswordResetForm(PasswordResetForm):
    """Password reset form with styled email field."""
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'you@example.com',
            'autocomplete': 'email',
        })
    )


class CustomSetPasswordForm(SetPasswordForm):
    """Set password form with styled fields."""
    new_password1 = forms.CharField(
        label=_("New Password"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': '••••••••',
            'autocomplete': 'new-password',
        }),
        strip=False,
    )
    new_password2 = forms.CharField(
        label=_("Confirm New Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': '••••••••',
            'autocomplete': 'new-password',
        }),
    )
