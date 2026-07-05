from django.contrib import admin
from .models import Category, SubCategory, Stock, CustomField, Template, AdvancedFilterSettings, Alert, ProductReview, DraftInvoice, DraftInvoiceItem

# Basic Admin Classes
admin.site.register(DraftInvoice)
admin.site.register(DraftInvoiceItem)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('cat_id', 'title', 'description')
    search_fields = ('title', 'description')

@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('subcat_id', 'title', 'category', 'description')
    search_fields = ('title', 'category__title')
    list_filter = ('category',)

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('stock_id', 'name', 'color', 'total_products', 'invested')
    search_fields = ('name', 'details')

@admin.register(CustomField)
class CustomFieldAdmin(admin.ModelAdmin):
    list_display = ('id', 'field_name', 'field_type', 'is_required')
    search_fields = ('field_name', 'field_type')

@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ('tem_id', 'template_name', 'keyvalue', 'type')
    search_fields = ('title', 'description', 'prod_id', 'tem_id')
    list_filter = ('category', 'subcategory', 'status', 'type')
    filter_horizontal = ('custom_fields',)



@admin.register(AdvancedFilterSettings)
class AdvancedFilterSettingsAdmin(admin.ModelAdmin):
    list_display = ['id']    

class AlertAdmin(admin.ModelAdmin):
    list_display = ('mtb_id', 'status', 'text', 'datetime', 'expiration_datetime')
    list_filter = ('status', 'datetime', 'expiration_datetime')
    search_fields = ('mtb_id', 'text')
    ordering = ('-datetime',)
    list_editable = ('status',)

admin.site.register(Alert, AlertAdmin)    



@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "rating",
        "name",
        "email",
        "is_approved",
        "created_at",
    )

    list_filter = (
        "is_approved",
        "rating",
        "created_at",
    )

    search_fields = (
        "product__title",
        "name",
        "email",
        "comment",
    )

    list_editable = (
        "is_approved",
    )

    readonly_fields = (
        "created_at",
    )

    ordering = ("-created_at",)

    fieldsets = (
        ("Product & User", {
            "fields": ("product", "user")
        }),
        ("Reviewer Info", {
            "fields": ("name", "email")
        }),
        ("Review Content", {
            "fields": ("rating", "comment")
        }),
        ("Moderation", {
            "fields": ("is_approved", "created_at")
        }),
    )