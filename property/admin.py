from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, PropertyType, Property, Landlord
# Register your models here.
# Register models with the admin site

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'name', 'date_of_birth', 'gender', 'role', 'is_active', 'is_staff')
    list_filter = ('is_active', 'is_staff', 'role')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('name', 'date_of_birth', 'gender', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'date_of_birth', 'gender', 'role', 'password1', 'password2', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}
        ),
    )
    search_fields = ('email', 'name')
    ordering = ('email',)

class PropertyTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'category', 'landlord', 'created_at', 'get_property_types')
    list_filter = ('category', 'property_type', 'landlord')
    search_fields = ('title', 'address')
    raw_id_fields = ('landlord',)
    date_hierarchy = 'created_at'

    def get_property_types(self, obj):
        return ", ".join([ptype.name for ptype in obj.property_type.all()])
    get_property_types.short_description = 'Property Types'  # Column name in admin

class LandlordAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email')
    search_fields = ('name', 'email')


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(PropertyType, PropertyTypeAdmin)
admin.site.register(Property, PropertyAdmin)
admin.site.register(Landlord, LandlordAdmin)