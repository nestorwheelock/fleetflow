from django import forms
from .models import LeadCapture, ReferralCredit


class SignupLeadForm(forms.ModelForm):
    """Form for capturing email leads from homepage."""

    class Meta:
        model = LeadCapture
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email',
                'required': True,
            })
        }


class ReferralForm(forms.ModelForm):
    """Form for submitting referrals."""

    class Meta:
        model = ReferralCredit
        fields = ['referrer_email', 'referred_email', 'referral_type']
        widgets = {
            'referrer_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your email address',
                'required': True,
            }),
            'referred_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Their email address',
                'required': True,
            }),
            'referral_type': forms.RadioSelect(attrs={
                'class': 'form-check-input',
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        referrer = cleaned_data.get('referrer_email')
        referred = cleaned_data.get('referred_email')

        if referrer and referred and referrer.lower() == referred.lower():
            raise forms.ValidationError("You cannot refer yourself.")

        return cleaned_data


class RentalSearchForm(forms.Form):
    """Form for searching rental companies by location."""

    location = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'City or ZIP code',
            'required': True,
        })
    )
    pickup_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'placeholder': 'Pickup date',
        })
    )
    return_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'placeholder': 'Return date',
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        pickup = cleaned_data.get('pickup_date')
        return_date = cleaned_data.get('return_date')

        if pickup and return_date and return_date < pickup:
            raise forms.ValidationError("Return date must be after pickup date.")

        return cleaned_data
