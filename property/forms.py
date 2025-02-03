from django import forms
from .models import CustomUser, Property, PropertyType
from django.core.exceptions import ValidationError
import re
from django.contrib.auth.forms import PasswordChangeForm


def clean_title(self):
        title = self.cleaned_data.get('title')
        if not title:
            raise forms.ValidationError("This field is required.")
        if len(title) < 5:
            raise forms.ValidationError("Title must be at least 5 characters long.")
        return title

def validate_zip_code(value):
    # Check if the value is all digits and matches either 5 or 6-4 format
    if not value.isdigit() or not re.match(r'^\d{5}(-\d{4})?$|^\d{6}$', value):
        raise ValidationError('Invalid ZIP code format. It should be 5 digits or 6-4 digits.')


def validate_first_name(value):
    # Check if the name contains only letters and starts with a letter
    if not re.match(r'^[A-Za-z][A-Za-z]*$', value):
        raise ValidationError('First name must start with a letter and contain only letters.')
    # Check if the name is longer than 15 characters
    if len(value) > 15:
        raise ValidationError('First name cannot be longer than 15 characters.')


class PropertyForm(forms.ModelForm):
    # Basic Info
    title = forms.CharField(
        max_length=35,
        label='Title',
        widget=forms.TextInput(attrs={'placeholder': 'Enter property title'})
    )

    # Category choices
    CATEGORY_CHOICES = (
        ('for_sale', 'For Sale'),
        ('for_rent', 'For Rent'),
    )
    category = forms.ChoiceField(choices=CATEGORY_CHOICES, label='Category')

    # Property Type choices
    property_type = forms.ModelMultipleChoiceField(
        queryset=PropertyType.objects.all(),  # Assuming PropertyType is the model for property types
        widget=forms.CheckboxSelectMultiple,
        label='Property Type'
    )

    # Location
    country = forms.ChoiceField(
        choices=[
            ('india', 'India'),
            ('usa', 'USA'),
            ('china', 'China'),
        ],
        label='Country'
    )
    city = forms.CharField(
        max_length=100,
        label='City',
        widget=forms.TextInput(attrs={'placeholder': 'Enter city'})
    )
    district = forms.CharField(
        max_length=100,
        label='District',
        widget=forms.TextInput(attrs={'placeholder': 'Enter district'})
    )
    zip_code = forms.CharField(
        max_length=10,
        label='Zip Code',
        widget=forms.TextInput(attrs={'placeholder': 'Enter zip code'}),
        validators=[validate_zip_code]
    )
    street_address = forms.CharField(
        max_length=300,
        label='Street Address',
        widget=forms.TextInput(attrs={'placeholder': 'Enter street address'})
    )
   
    # Price
    currency = forms.ChoiceField(
        choices=[
            ('usd', 'USD'),
            ('inr', 'INR'),
            ('cny', 'CNY'),
        ],
        label='Currency'
    )
    price = forms.DecimalField(max_digits=10, decimal_places=2, label='Price')

    FREQUENCY_CHOICES = (
        ('per_month', 'Per Month'),
        ('per_year', 'Per Year'),
        ('per_day', 'Per Day'),
    )
    frequency = forms.ChoiceField(choices=FREQUENCY_CHOICES, label='Frequency')

    # Photos
    photos = forms.FileField(label='Upload Photos', required=False)

    # Contact Information
    first_name = forms.CharField(
        max_length=100,
        label='First Name',
        widget=forms.TextInput(attrs={'placeholder': 'Enter your first name'}),
        validators=[validate_first_name]
    )
    contact_email = forms.EmailField(  # Change 'email' to 'contact_email'
        label='Email',
        widget=forms.EmailInput(attrs={'placeholder': 'Enter your email'})
    )
    phone_number = forms.CharField(
        max_length=15,
        label='Phone Number',
        widget=forms.TextInput(attrs={'placeholder': 'Enter your phone number'})
    )

    class Meta:
        model = Property
        fields = [
            'title', 'category', 'property_type',
            'country', 'city', 'district',
            'zip_code', 'street_address','latitude', 'longitude',
            'currency', 'price', 'frequency',
            'photos',
            'first_name', 'contact_email', 'phone_number'  # Add contact fields to the form
        ]

class PropertySearchForm(forms.Form):
    query = forms.CharField(label='Search', max_length=100, required=False)