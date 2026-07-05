from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # Fields to show in list display
    list_display = (
        'username', 'email', 'first_name', 'last_name',
        'mobile_number', 'account_type', 'role', 'mtb_id', 'is_active', 'is_staff'
    )

    # Fields to filter in admin
    list_filter = ('account_type', 'role', 'is_staff', 'is_superuser', 'is_active')

    # Fields searchable via search bar
    search_fields = ('username', 'email', 'mobile_number', 'mtb_id')

    # Field ordering in the list display
    ordering = ('date_joined',)

    # Read-only fields
    readonly_fields = ('mtb_id',)

    # Add extra fields to the user creation/edit forms
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('mobile_number','cnic', 'account_type', 'role', 'mtb_id','user_pass','profile_pic', 'address'),
        }),
        ('Merchant', {
            'fields': ('merchant_balance',),
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('mobile_number', 'account_type', 'role','user_pass'),
        }),
          ('Merchant', {
            'fields': ('merchant_balance',),
        }),
    )

 