from django.db import models
import uuid
# Create your models here.


def generate_invoice_uuid():
    from .models import Invoice  # Avoid circular import if inside models.py

    while True:
        new_id = f"INV{uuid.uuid4().hex[:6]}"
        if not Invoice.objects.filter(invoice_id=new_id).exists():
            return new_id
        





class Invoice(models.Model):
    invoice_id = models.CharField(max_length=20, default=generate_invoice_uuid, editable=False)
    stock_id = models.CharField(max_length=100, blank=True, null=True, default="")
    merchant_id = models.CharField(max_length=100, blank=True, null=True, default="")

    total = models.CharField(max_length=100, blank=True, null=True, default="0")
    debit = models.CharField(max_length=100, blank=True, null=True, default="0")
    credit = models.CharField(max_length=100, blank=True, null=True, default="0")
    balance = models.CharField(max_length=100, blank=True, null=True, default="0")

    date = models.CharField(max_length=50, blank=True, null=True, default="")

    # payment details
    payment_method = models.CharField(max_length=100, blank=True, null=True, default="")
    payment_reference = models.CharField(max_length=100, blank=True, null=True, default="")
    payment_to = models.CharField(max_length=100, blank=True, null=True, default="")

    source_type = models.CharField(max_length=100, blank=True, null=True, default="")

    # stock details
    stock_handler = models.CharField(max_length=100, blank=True, null=True, default="")
    stock_location = models.CharField(max_length=100, blank=True, null=True, default="")
    stock_source = models.CharField(max_length=100, blank=True, null=True, default="")


    def __str__(self):
        return self.invoice_id

class InvoiceItem(models.Model):
    # One invoice → many items
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='items'
    )

    # Display fields on invoice
    product_name = models.CharField(max_length=255, blank=True, null=True)
    rate         = models.CharField(max_length=100, blank=True, null=True, default="0")      # or DecimalField
    quantity     = models.CharField(max_length=100, blank=True, null=True, default="0")      # or IntegerField
    amount       = models.CharField(max_length=100, blank=True, null=True, default="0")      # rate * quantity

    # Real product code so you can link back to actual product
    product_code = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Real product/template code to view full product details."
    )

    def __str__(self):
        return f"{self.product_name} ({self.invoice.invoice_id})"
