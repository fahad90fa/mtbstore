from django.db import models

from accounts.models import CustomUser

# Create your models here.
class EmployeeEntry(models.Model):
    ENTRY_TYPES = (
        ("CLIENT", "Client Sale"),
        ("MERCHANT", "Merchant"),
        ("STOCK", "Stock Entry"),
        ("OTHER", "Other"),
    )

    employee = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={"account_type": "Employee"},
        related_name="entries"
    )

    entry_type = models.CharField(
        max_length=20,
        choices=ENTRY_TYPES
    )

    # Optional customer (client or merchant)
    customer = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employee_entries"
    )

    date = models.DateField()

    # Single line summary
    title = models.CharField(
        max_length=255,
        help_text="Short title, e.g. Cement sale, Grocery stock"
    )

    # BIG box for copy-paste product list
    details = models.TextField(
        help_text="Paste full product list here"
    )

    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.username} | {self.entry_type} | {self.date}"

