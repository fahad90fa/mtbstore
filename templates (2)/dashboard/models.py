from django.db import models
import uuid
import json
from django.utils.text import slugify
from django.conf import settings
from decimal import Decimal

from accounts.models import CustomUser
from merchants.models import generate_invoice_uuid


def generate_stock_uuid():
    from .models import Stock  # Avoid circular import if inside models.py

    while True:
        new_id = f"STOCK{uuid.uuid4().hex[:10]}"
        if not Stock.objects.filter(stock_id=new_id).exists():
            return new_id


def generate_tem_uuid():
    from .models import Template  # Avoid circular import if inside models.py

    while True:
        new_id = f"TEM{uuid.uuid4().hex[:10]}"
        if not Template.objects.filter(tem_id=new_id).exists():
            return new_id

def generate_prod_uuid():
    from .models import Template  # Avoid circular import if inside models.py

    while True:
        new_id = f"PROD{uuid.uuid4().hex[:10]}"
        if not Template.objects.filter(prod_id=new_id).exists():
            return new_id




def generate_cat_uuid():
    from .models import Category  # Avoid circular import if inside models.py

    while True:
        new_id = f"CAT{uuid.uuid4().hex[:10]}"
        if not Category.objects.filter(cat_id=new_id).exists():
            return new_id








class Alert(models.Model):
    # Choices for the alert status
    STATUS_CHOICES = [
        ('read', 'Read'),
        ('sent', 'Sent'),
        ('awaiting', 'Awaiting'),
    ]

    mtb_id = models.CharField(max_length=255, unique=False)  
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='awaiting')  
    text = models.TextField() 
    datetime = models.DateTimeField(auto_now_add=True)  
    expiration_datetime = models.DateTimeField(null=True, blank=True)  

    def __str__(self):
        return f"Alert {self.mtb_id} - {self.status}"

    class Meta:
        ordering = ['-datetime']  # Order by most recent datetime



class Category(models.Model):
    cat_id = models.CharField(max_length=20, default=generate_cat_uuid, editable=False)

    tem_id = models.CharField(max_length=100, blank=True, null=True)
    img = models.FileField(upload_to='category/', blank=True, null=True)
    title = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    status = models.CharField(max_length=50, default="inactive", blank=True, null=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1

            while Category.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class SubCategory(models.Model):
    subcat_id = models.AutoField(primary_key=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')

    title = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(max_length=120, blank=True)

    class Meta:
        unique_together = ('category', 'slug')

    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1

            while SubCategory.objects.filter(
                category=self.category,
                slug=slug
            ).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.category.title} - {self.title}"


class Stock(models.Model):
    stock_id = models.CharField(max_length=20, default=generate_stock_uuid, editable=False)

    name = models.CharField(max_length=100, blank=True, null=True)
    color = models.CharField(max_length=100, blank=True, null=True)

    total_products = models.CharField(max_length=100, default="00", blank=True, null=True)
    invested = models.CharField(max_length=100, default="00", blank=True, null=True)

    sold_product = models.CharField(max_length=100, default="00", blank=True, null=True)
    mtb_id = models.CharField(max_length=100, default="00", blank=True, null=True)

    details = models.TextField(blank=True)
    
    def __str__(self):
        return self.name





class CustomField(models.Model):
    field_name = models.CharField(max_length=100, blank=True, null=True)
    field_type = models.CharField(max_length=100, blank=True, null=True)
    is_required = models.CharField(max_length=255, blank=True, null=True)
    default_value = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return f"{self.field_name} - {self.field_type} - {self.is_required}"


class Template(models.Model):
    type = models.CharField(max_length=50, default="product", blank=True, null=True)

    tem_id = models.CharField(max_length=20, default=generate_tem_uuid, editable=False)
    template_name = models.CharField(max_length=100, default="noname", blank=True, null=True)
    color = models.CharField(max_length=100, blank=True, null=True)
    totalbalance = models.CharField(max_length=100, default="00", blank=True, null=True)

    keyvalue = models.CharField(max_length=100, blank=True, null=True)
    keyvalue_required = models.CharField(max_length=100, blank=True, null=True)

    total_category = models.CharField(max_length=100, default="00", blank=True, null=True)
    total_subcategory = models.CharField(max_length=100, default="00", blank=True, null=True)

    sold_product = models.CharField(max_length=100, default="00", blank=True, null=True)
    total_product = models.CharField(max_length=100, default="00", blank=True, null=True)

    # For product
    category = models.ManyToManyField(Category, blank=True)
    subcategory = models.ManyToManyField(SubCategory, blank=True)
    stock = models.ForeignKey(Stock, on_delete=models.SET_NULL, blank=True, null=True)
    # For product

    
    # Fixed fields that all products will have
    prod_id = models.CharField(max_length=100, default=generate_prod_uuid, blank=True, null=True)
    title = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    img = models.FileField(upload_to='products/', blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True)

    # price calculation
    base_price_pre = models.CharField(max_length=100, blank=True, null=True)
    base_price_percentage = models.CharField(max_length=50, blank=True, null=True)
    base_price_percentage_sign = models.CharField(max_length=50, blank=True, null=True)
    base_price = models.CharField(max_length=100, blank=True, null=True)
    show_price = models.CharField(max_length=100, blank=True, null=True)

    # stock
    available_product = models.CharField(max_length=50, default="00", blank=True, null=True)
    sold_product = models.CharField(max_length=50, default="00", blank=True, null=True)
    stock_product = models.CharField(max_length=50, default="00", blank=True, null=True)

    # Custom Fields (MANY-TO-MANY)
    custom_fields = models.ManyToManyField(CustomField, blank=True)

    tags = models.CharField(max_length=255, blank=True, null=True)
    
    created_at = models.CharField(max_length=100, blank=True, null=True)
    updated_at = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return self.template_name or "Unnamed Template"



class AdvancedFilterSettings(models.Model):
    filters = models.JSONField(default=dict)  # All filter values stored as JSON

    def save(self, *args, **kwargs):
        # Force only one row (singleton)
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_solo(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "Advanced Filter Settings"



class ProductReview(models.Model):
    product = models.ForeignKey(
        Template,
        on_delete=models.CASCADE,
        related_name="reviews",
        limit_choices_to={"type": "product"}
    )

    # Optional user (guest reviews allowed)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    name = models.CharField(max_length=100)
    email = models.EmailField()

    rating = models.PositiveSmallIntegerField(
        choices=[(i, i) for i in range(1, 6)]
    )

    comment = models.TextField(blank=True)

    is_approved = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.title} - {self.rating}★"
    

class DraftInvoice(models.Model):
    draft_id = models.CharField(
        max_length=20,
        default=generate_invoice_uuid,
        editable=False,
        unique=True
    )

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="draft_invoices"
    )

    client_id = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        default="draft"
    )  # draft | abandoned

    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    payment_method = models.CharField(max_length=100, blank=True, null=True, default="")
    payment_reference = models.CharField(max_length=100, blank=True, null=True, default="")
    date = models.CharField(max_length=50, blank=True, null=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Draft {self.draft_id}"

class DraftInvoiceItem(models.Model):
    draft = models.ForeignKey(
        DraftInvoice,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product_id = models.CharField(max_length=100)
    product_name = models.CharField(max_length=255)

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    quantity = models.PositiveIntegerField(default=1)

    total = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def save(self, *args, **kwargs):
        try:
            price = Decimal(self.price or "0")
            qty = Decimal(self.quantity or "0")
            self.total = str(price * qty)
        except Exception:
            self.total = "0"

        super().save(*args, **kwargs)
