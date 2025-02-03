from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from geopy.geocoders import Nominatim

PROPERTY_TYPE_CHOICES = (
    ('house', 'House'),
    ('apartment', 'Apartment'),
    ('room', 'Room'),
    ('office', 'Office'),
)

# Custom user manager
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

# Custom user model
class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('landlord', 'Landlord'),
        ('tenant', 'Tenant'),
    )

    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'date_of_birth', 'gender', 'role']

    objects = CustomUserManager()

    def __str__(self):
        return self.email

class PropertyType(models.Model):
    name = models.CharField(max_length=10, choices=PROPERTY_TYPE_CHOICES, null=True)

    def __str__(self):
        return self.get_name_display() 

class Property(models.Model):
    LANDLORD_USER = 'landlord'

    CATEGORY_CHOICES = (
        ('for_sale', 'For Sale'),
        ('for_rent', 'For Rent'),
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    address = models.CharField(max_length=300)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    property_type = models.ManyToManyField(PropertyType)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    street_address = models.CharField(max_length=300)

    
     
    
    currency = models.CharField(max_length=10)  # Currency like USD, INR etc.
    
    frequency = models.CharField(max_length=10, choices=[
        ('per_month', 'Per Month'),
        ('per_year', 'Per Year'),
        ('per_day', 'Per Day'),
    ])
    
    photos = models.ImageField(upload_to='property_photos/', blank=True, null=True)
    videos = models.FileField(upload_to='property_videos/', blank=True, null=True)
    
    first_name = models.CharField(max_length=100)  # New field for first name
    contact_email = models.EmailField()             # Changed to avoid conflict with user email
    phone_number = models.CharField(max_length=15)  # New field for phone number
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    landlord = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': LANDLORD_USER})

    def __str__(self):
        return self.title


class Landlord(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    image = models.ImageField(upload_to='landlord_images/')
    description = models.TextField()

    def __str__(self):
        return self.name
    

def geocode_address(self):
        if not self.latitude or not self.longitude:
            geolocator = Nominatim(user_agent="property")
            full_address = f"{self.street_address}, {self.city}, {self.country}"
            location = geolocator.geocode(full_address)
            if location:
                self.latitude = location.latitude
                self.longitude = location.longitude
                self.save(update_fields=['latitude', 'longitude'])

def __str__(self):
    return self.title
