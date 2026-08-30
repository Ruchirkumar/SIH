from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # Display the role in the user list view
    list_display = ('username', 'email', 'role', 'is_staff', 'is_superuser')

    # Add the role field to the User edit page
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Information', {'fields': ('role',)}),
    )

    # Add the role field to the User creation page
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Information', {'fields': ('role',)}),
    )
