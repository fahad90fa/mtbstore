from django.contrib import admin
from .models import Invoice, InvoiceItem


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("invoice_id", "stock_id", "total", "debit", "credit", "balance")
    search_fields = ("invoice_id", "stock_id", "merchant_id")
    list_filter = ("invoice_id",)
    ordering = ("-invoice_id",)


@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = (
        "invoice",
        "product_name",
        "product_code",
        "rate",
        "quantity",
        "amount",
    )
    search_fields = (
        "product_name",
        "product_code",
        "invoice__invoice_id",
    )
    list_filter = ("invoice",)
