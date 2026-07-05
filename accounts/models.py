from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

def generate_mtb_uuid():
    from .models import CustomUser  # Avoid circular import if inside models.py

    while True:
        new_id = f"MTB{uuid.uuid4().hex[:10]}"
        if not CustomUser.objects.filter(mtb_id=new_id).exists():
            return new_id
    
class CustomUser(AbstractUser):
    mtb_id = models.CharField(max_length=20, default=generate_mtb_uuid, editable=False)
    profile_pic = models.FileField(upload_to='accounts/', blank=True, null=True)
    account_type = models.CharField(max_length=100, blank=True, null=True) # Merchant, Client, Employee
    role = models.CharField(max_length=100, blank=True, null=True)
    mobile_number = models.CharField(max_length=20, blank=True, null=True, unique=True)
    cnic = models.CharField(max_length=30, blank=True, null=True, unique=True)
    user_pass = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=250, blank=True, null=True, default="")

    # date
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    # for Merchant
    status = models.CharField(max_length=100, blank=True, null=True,  default="Offline") # Online, Offline
    merchant_balance = models.CharField(max_length=100, blank=True, null=True, default="0")

    # for Clients
    total_orders = models.CharField(max_length=100, blank=True, null=True)
    client_balance = models.CharField(max_length=100, blank=True, null=True, default="0")

    # for Employees
    salary = models.CharField(max_length=100, blank=True, null=True)