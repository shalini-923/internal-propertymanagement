# Create your views here.
from django.conf import settings
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import HttpResponse
from .models import CustomUser ,Property, PropertyType
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .forms import PropertyForm 
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.contrib.auth import update_session_auth_hash
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.contrib.auth.views import PasswordResetView
import requests
from .forms import PropertySearchForm




def index(request):
    return render(request, 'property/index.html')


def property_search(request):
    return render(request, 'property/index.html') 


def property_search_results(request):
    # Get search parameters from the request
    keyword = request.GET.get('keyword', '')
    category = request.GET.get('category', '')
    country = request.GET.get('country', '')
    city = request.GET.get('city', '')
    district = request.GET.get('district', '')
    max_price = request.GET.get('max_price', None)
    frequency = request.GET.get('frequency', '')

    # Filter properties based on the search parameters
    properties = Property.objects.all()  # Start with all properties

    if keyword:
        properties = properties.filter(title__icontains=keyword)  # Assuming title is a field in your Property model

    if category:
        properties = properties.filter(category=category)

    if country:
        properties = properties.filter(country=country)

    if city:
        properties = properties.filter(city__icontains=city)

    if district:
        properties = properties.filter(district__icontains=district)

    if max_price:
        properties = properties.filter(price__lte=max_price)

    if frequency:
        properties = properties.filter(frequency=frequency)

    context = {
        'properties': properties  # Pass the filtered properties to the template
    }
    return render(request, 'property/property_search_results.html', context)  # Replace with your actual results template name

def about(request):
    # Filter landlords
    landlords = CustomUser.objects.filter(role='landlord', is_active=True)
    
    context = {
        'landlords': landlords,
    }
    
    return render(request, 'property/about.html', context)

def contact(request):
    return render(request, 'property/contact.html')

def agents(request):
    # Filter landlords
    landlords = CustomUser.objects.filter(role='landlord', is_active=True)
    
    context = {
        'landlords': landlords,
    }
    
    return render(request, 'property/agents-grid.html', context)

def agent_single(request, id):
    # Fetch the agent based on the given ID or return a 404 error if not found
    agent = get_object_or_404(agent, id=id)
    
    # Pass the agent data to the template
    return render(request, 'property/agent-single.html', {'agent': agent})

def property_grid(request):
    # Retrieve all properties and order them by ID
    properties = Property.objects.all().order_by('id')
    
    # Filtering by location
    location = request.GET.get('location')
    if location:
        properties = properties.filter(city=location)  # Adjust based on your model field

    # Filtering by property type
    property_types = request.GET.getlist('property_types')
    if property_types:
        properties = properties.filter(property_type__name__in=property_types).distinct()

    # Filtering by price
    price = request.GET.get('price')
    if price:
        properties = properties.filter(price__lte=price)

    # Check the current view type (default to grid view)
    view_type = request.GET.get('view_type', 'grid')


    # Create a Paginator object to manage pagination (6 properties per page)
    paginator = Paginator(properties, 6)  
    page_number = request.GET.get('page')  # Get the current page number from the request
    page_obj = paginator.get_page(page_number)  # Get the properties for the current page
    
    # Prepare the context for rendering the template
    context = {
        'page_obj': page_obj,
        'location': location,
        'property_types': property_types,
        'price': price,
        'view_type': view_type,  # Add this line
    }
    
    # Render the 'property_grid.html' template with the context
    return render(request, 'property_grid.html', context)

def property_single(request, property_id):
    property_instance = get_object_or_404(Property, id=property_id)
    
    # Ensure that latitude and longitude are set (you can add additional checks if needed)
    if not property_instance.latitude or not property_instance.longitude:
        # Handle the case where latitude or longitude is not set
        # You can either set defaults or display an error message
        latitude = 0  # Default or fallback value
        longitude = 0  # Default or fallback value
    else:
        latitude = property_instance.latitude
        longitude = property_instance.longitude

     # Check if the logged-in user is the landlord of the property or has a 'landlord' role
    user_is_landlord = request.user.role == 'landlord' and request.user == property_instance.landlord


    return render(request, 'property/property-single.html', {
        'property': property_instance,
        'latitude': latitude,
        'longitude': longitude,
        'user_is_landlord': user_is_landlord,
    })

def property_edit(request, property_id):
    property_instance = get_object_or_404(Property, id=property_id)

    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES, instance=property_instance)
        if form.is_valid():
            form.save()
            return redirect('property_grid')
        else:
            print(form.errors)  # Print out errors for debugging
    else:
        form = PropertyForm(instance=property_instance)

    context = {
        'form': form,
        'property': property_instance
    }

    return render(request, 'property/property_edit.html', context)

def property_delete(request, property_id):
    property_instance = get_object_or_404(Property, id=property_id)
    
    if request.method == 'POST':
        property_instance.delete()
        messages.success(request, "Property deleted successfully.")
        return redirect('property_grid')  # Redirect to the property grid after deletion

    return render(request, 'property/property_delete_confirm.html', {'property': property_instance})

def blog_grid(request):
    return render(request, 'property/blog-grid.html')

def blog_single(request, id):
    # Add logic to fetch the blog post based on the ID
    return render(request, 'property/blog-single.html', {'blog_id': id})

def sign_in(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Use authenticate to check credentials
        user = authenticate(request, username=email, password=password)
        print(user)
        if user is not None:
            print("User authenticated:", user.email)  # Debug message
            login(request, user)  # Log the user in
            
            # Redirect based on user role
            if user.role == 'landlord':
                return redirect('landlord_dashboard')
            elif user.role == 'tenant':
                return redirect('tenant_dashboard')
            else:
                messages.error(request, "User role is not recognized.")
        else:
            messages.error(request, "Invalid email or password.")

    return render(request, 'property/sign_in.html')


def sign_up(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm-password')
        dob = request.POST.get('dob')
        gender = request.POST.get('gender')
        role = request.POST.get('role')

        if password == confirm_password:
            user = CustomUser(
                name=name,
                email=email,
                gender=gender,
                date_of_birth=dob,
                role=role
            )
            user.set_password(password)  # Hash the password
            user.save()
            return redirect('sign_in')  # Redirect to sign-in page after successful registration
        else:
            return HttpResponse("Passwords do not match!")  # Handle error

    return render(request, 'property/sign_up.html')  # Render signup p



def forgot_password(request):
    return render(request, 'forgot_password.html')  # You can create a new template for this


 # Ensure that the user is logged in
@login_required
def landlord_dashboard(request):
    # Start with all properties owned by the logged-in landlord
    properties = Property.objects.filter(landlord=request.user).order_by('id')

    # Handle filtering by location
    location = request.GET.get('location')
    if location:
        properties = properties.filter(city__iexact=location)

    # Handle filtering by property types
    property_type = request.GET.getlist('property_type')
    if property_type:
        properties = properties.filter(property_type__name__in=property_type).distinct()

    # Handle filtering by price
    price = request.GET.get('price')
    if price:
        properties = properties.filter(price__lte=price)

    # Create a Paginator object to manage pagination (6 properties per page)
    paginator = Paginator(properties, 6)  
    page_number = request.GET.get('page')  # Get the current page number from the request
    page_obj = paginator.get_page(page_number)  # Get the properties for the current page

    # Prepare the context for rendering the template
    context = {
        'page_obj': page_obj,
        'property_type_choices': PropertyType.objects.all(),  # Pass available property types to the template
    }
    
    # Render the 'landlord_dashboard.html' template with the context
    return render(request, 'property/landlord_dashboard.html', context)


@login_required
def add_property(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)  # Include FILES for media uploads
        if form.is_valid():
            # Create a new Property instance
            property_instance = form.save(commit=False)
            property_instance.landlord = request.user  # Assign the logged-in user as landlord
            
            # Fetch location details for latitude and longitude
            location = f"{form.cleaned_data['city']}, {form.cleaned_data['district']}, {form.cleaned_data['country']}"
            nominatim_url = f'https://nominatim.openstreetmap.org/search?city={form.cleaned_data["city"]}&country={form.cleaned_data["country"]}&format=json'
            response = requests.get(nominatim_url).json()
            if response:
                property_instance.latitude = response[0]['lat']
                property_instance.longitude = response[0]['lon']
            else:
                property_instance.latitude = None  # Set to None if not found
                property_instance.longitude = None  # Set to None if not found

            # Save the property instance to the database
            property_instance.save()

            # Handle property types separately if using ManyToManyField
            property_instance.property_type.set(form.cleaned_data['property_type'])

            # Redirect to the property grid after successful addition
            return redirect('property_grid')  # Adjust the URL name as needed
        else:
            # The form is not valid, so we re-render the form with errors
            print(form.errors)

    else:
        form = PropertyForm()  # Create a blank form for GET requests

    context = {
        'form': form,
    }
    return render(request, 'property/add_property.html', context)

@login_required
def tenant_dashboard(request):
    form = PropertySearchForm(request.GET or None)
    properties = Property.objects.all()

    if form.is_valid():
        query = form.cleaned_data['query']
        if query:
            properties = properties.filter(title__icontains=query)  # Search by title

    context = {
        'form': form,
        'properties': properties,
    }
    return render(request, 'property/tenant_dashboard.html', context)

def logout_view(request):
    logout(request)
    return redirect('login')  # Redirect to login page after logout

@login_required
def edit_profile(request):
    user = request.user

    if request.method == 'POST':
        if 'cancel' in request.POST:
            return redirect('landlord_dashboard' if user.role == 'landlord' else 'tenant_dashboard')

        # Update user details
        user.username = request.POST.get('username', user.username)
        user.email = request.POST.get('email', user.email)
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)

        # Handle password change
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')

        if old_password and new_password1 and new_password2:
            if new_password1 == new_password2:
                if user.check_password(old_password):
                    user.set_password(new_password1)
                    user.save()
                    update_session_auth_hash(request, user)
                    messages.success(request, 'Your password has been updated successfully.')
                else:
                    messages.error(request, 'Old password is incorrect.')
            else:
                messages.error(request, 'New passwords do not match.')

        user.save()  # Save user details after all updates
        messages.success(request, 'Your profile has been updated successfully.')

        # Redirect based on the user's role
        return redirect('landlord_dashboard' if user.role == 'landlord' else 'tenant_dashboard')

    return render(request, 'property/edit_profile.html', {'user': user})

def custom_logout(request):
    logout(request)
    return redirect('sign_in')

class CustomPasswordResetView(PasswordResetView):
    template_name = '  password_reset_form.html'
    email_template_name = 'password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')
    subject_template_name = 'password_reset_subject.txt'

    # Customizing the email sending logic
    def form_valid(self, form):
        email = form.cleaned_data['email']
        # Check if the email exists in your system
        send_mail(
            'Password Reset Request',
            'You requested a password reset. Click the link below to reset your password.',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        return super().form_valid(form)

def send_message(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        subject = request.POST['subject']
        message = request.POST['message']

        try:
            send_mail(
                subject,
                message,
                email,
                ['your-email@example.com'],  # Replace with your email
                fail_silently=False,
            )
            return HttpResponse("Your message has been sent. Thank you!")
        except Exception as e:
            return HttpResponse(f"Error: {str(e)}")  
    



from rest_framework import generics, permissions, status
from rest_framework.response import Response 
from .models import Property
from .serializers import CustomUserLoginSerializer, CustomUserSerializer, PropertySerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView



class PropertyCreateView(generics.GenericAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [permissions.AllowAny]  # Allow access to anyone

    @swagger_auto_schema(
        operation_description="Retrieve all properties",
        responses={200: PropertySerializer(many=True)},
    )

    def get(self, request, *args, **kwargs):
        # View all properties
        properties = self.get_queryset()
        serializer = self.get_serializer(properties, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_description="Create a new property",
        request_body=PropertySerializer,
        responses={201: PropertySerializer},
    )

    def post(self, request, *args, **kwargs):
        # Allow anyone to create a property
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        # Save the property instance
        serializer.save()

class PropertyListView(generics.GenericAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [permissions.AllowAny]  # Allow access to anyone

    @swagger_auto_schema(
        operation_description="Retrieve a single property by ID or list all properties with optional filtering.",
        manual_parameters=[
            openapi.Parameter(
                'pk', openapi.IN_PATH, description="ID of the property to retrieve", type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'price_min', openapi.IN_QUERY, description="Minimum price filter", type=openapi.TYPE_NUMBER
            ),
            openapi.Parameter(
                'price_max', openapi.IN_QUERY, description="Maximum price filter", type=openapi.TYPE_NUMBER
            ),
            openapi.Parameter(
                'property_type', openapi.IN_QUERY, description="Filter by property type ID", type=openapi.TYPE_INTEGER
            )
        ],
        responses={
            200: PropertySerializer(many=True),
            404: 'Not found'
        }
    )

    def get(self, request, *args, **kwargs):
        property_id = kwargs.get('pk')

        if property_id:
            # Retrieve a single property
            property_instance = self.get_queryset().filter(id=property_id).first()
            if property_instance:
                serializer = self.get_serializer(property_instance)
                return Response(serializer.data)
            else:
                return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        else:
            # List all properties with optional filtering
            properties = self.get_queryset()

            # Apply filtering based on query parameters
            price_min = request.query_params.get('price_min')
            price_max = request.query_params.get('price_max')
            property_type = request.query_params.get('property_type')

            if price_min is not None:
                properties = properties.filter(price__gte=price_min)

            if price_max is not None:
                properties = properties.filter(price__lte=price_max)

            if property_type is not None:
                properties = properties.filter(property_type__id=property_type)

            serializer = self.get_serializer(properties, many=True)
            return Response(serializer.data)

class PropertyUpdateView(generics.GenericAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [permissions.AllowAny]  # Allow access to anyone

    @swagger_auto_schema(
        operation_description="Retrieve details of a specific property by its ID.",
        manual_parameters=[
            openapi.Parameter(
                'pk', openapi.IN_PATH, description="ID of the property to retrieve", type=openapi.TYPE_INTEGER
            )
        ],
        responses={
            200: PropertySerializer,
            404: 'Not found'
        }
    )

    def get(self, request, *args, **kwargs):
        # Retrieve the property details
        property_id = kwargs.get('pk')
        property_instance = self.get_queryset().filter(id=property_id).first()

        if property_instance:
            serializer = self.get_serializer(property_instance)
            return Response(serializer.data)
        else:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        
    @swagger_auto_schema(
        operation_description="Update details of a specific property by its ID.",
        manual_parameters=[
            openapi.Parameter(
                'pk', openapi.IN_PATH, description="ID of the property to update", type=openapi.TYPE_INTEGER
            )
        ],
        request_body=PropertySerializer,
        responses={
            200: PropertySerializer,
            404: 'Not found'
        }
    )

    def put(self, request, *args, **kwargs):
        # Update property details
        property_id = kwargs.get('pk')
        property_instance = self.get_queryset().filter(id=property_id).first()

        if property_instance:
            serializer = self.get_serializer(property_instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        else:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

    def perform_update(self, serializer):
        # Save updates to the property
        serializer.save()

class PropertyDeleteView(generics.GenericAPIView):
    queryset = Property.objects.all()
    permission_classes = [permissions.AllowAny]  # Allow access to anyone

    @swagger_auto_schema(
        operation_description="Delete a specific property by its ID.",
        manual_parameters=[
            openapi.Parameter(
                'pk', openapi.IN_PATH, description="ID of the property to delete", type=openapi.TYPE_INTEGER
            )
        ],
        responses={
            204: 'Deleted successfully',
            404: 'Not found'
        }
    )

    def delete(self, request, *args, **kwargs):
        # Delete a property
        property_id = kwargs.get('pk')
        property_instance = self.get_queryset().filter(id=property_id).first()

        if property_instance:
            self.perform_destroy(property_instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

    def perform_destroy(self, instance):
        # Delete the property instance
        instance.delete()


class RegisterView(generics.CreateAPIView):
    """
    API view for user registration.
    """
    serializer_class = CustomUserSerializer

    @swagger_auto_schema(
        operation_description="Register a new user.",
        request_body=CustomUserSerializer,
        responses={
            201: openapi.Response(
                description="User registered successfully",
                schema=CustomUserSerializer
            ),
            400: "Invalid data"
        }
    )

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({'id': user.id, 'email': user.email}, status=status.HTTP_201_CREATED)
    


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    API view for user login with custom response.
    """
    serializer_class = CustomUserLoginSerializer  # Use the custom serializer

    @swagger_auto_schema(
        operation_description="User login.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='User email'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='User password'),
            },
            required=['email', 'password'],
        ),
        responses={
            200: openapi.Response(
                description="Login successful",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token'),
                        'access': openapi.Schema(type=openapi.TYPE_STRING, description='Access token'),
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='User ID'),
                        'email': openapi.Schema(type=openapi.TYPE_STRING, description='User email'),
                    }
                )
            ),
            401: "Invalid credentials",
            404: "User not found",
        }
    )

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data.get('user')  # Safely get user from validated data

        refresh = RefreshToken.for_user(user)  # Generate refresh token

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),  # Generate access token
            'id': user.id,
            'email': user.email,
        }, status=status.HTTP_200_OK)