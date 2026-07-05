# admin.py
from django.contrib import admin
from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "phone", "is_read", "created_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("full_name", "email", "phone", "message")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)

    actions = ("mark_as_read", "mark_as_unread")

    @admin.action(description="Mark selected messages as read")
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)

    @admin.action(description="Mark selected messages as unread")
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
