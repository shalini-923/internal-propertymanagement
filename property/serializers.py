from rest_framework import serializers
from .models import Property, PropertyType, CustomUser
from django.contrib.auth import get_user_model

class PropertyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyType
        fields = '__all__'

class PropertySerializer(serializers.ModelSerializer):
    # Use PrimaryKeyRelatedField for ManyToMany relationships
    property_type = serializers.PrimaryKeyRelatedField(queryset=PropertyType.objects.all(), many=True)

    class Meta:
        model = Property
        fields = '__all__'

    def create(self, validated_data):
        # Extract property_type data
        property_type_data = validated_data.pop('property_type')
        
        # Create the Property instance
        property_instance = Property.objects.create(**validated_data)
        
        # Set the ManyToMany field with provided data
        property_instance.property_type.set(property_type_data)
        
        return property_instance

    def update(self, instance, validated_data):
        # Extract property_type data if present
        property_type_data = validated_data.pop('property_type', None)
        
        # Update the Property instance fields
        instance = super().update(instance, validated_data)
        
        # If property_type data is provided, update the ManyToMany field
        if property_type_data is not None:
            instance.property_type.set(property_type_data)
        
        return instance
        
class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'name', 'email', 'role']

from rest_framework import serializers
from .models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'name', 'email', 'date_of_birth', 'gender', 'role', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = CustomUser(
            email=validated_data['email'],
            name=validated_data['name'],
            date_of_birth=validated_data['date_of_birth'],
            gender=validated_data['gender'],
            role=validated_data['role'],
        )
        user.set_password(validated_data['password'])  # Hash the password
        user.save()
        return user

# Get the custom user model
CustomUser = get_user_model()

class CustomUserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = CustomUser.objects.filter(email=email).first()
            if user and user.check_password(password):
                return {'user': user}  # Return a dictionary with the user
            raise serializers.ValidationError("Invalid email or password.")
        raise serializers.ValidationError("Email and password are required.")