from django.forms import IntegerField
from django.shortcuts import render, HttpResponse, get_object_or_404, redirect
from accounts.decorator import superadmin_required
from django.views.decorators.http import require_POST
from django.utils.timezone import now
from .models import Alert, DraftInvoice, Template, Stock
from django.http import JsonResponse
from ecom.models import ContactMessage
from django.db.models import Count
from django.db.models.functions import Cast
from django.utils import timezone
from datetime import timedelta
from accounts.models import CustomUser
from django.db import models
from django.db.models import Count, Q

from merchants.models import Invoice, InvoiceItem
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from datetime import datetime, timedelta
from decimal import Decimal

@superadmin_required
def Dashboard(request):
    users = CustomUser.objects.aggregate(
        total_users=Count("id"),
        total_merchants=Count("id", filter=models.Q(account_type="Merchant")),
        total_clients=Count("id", filter=models.Q(account_type="Client")),
        total_employees=Count("id", filter=models.Q(account_type="Employee")),
    )
    data = Template.objects.aggregate(
        total_products=Count("id", filter=Q(type="product")),
        total_templates=Count("id", filter=Q(type="template")),
    )

    total_stocks = Stock.objects.count()
    

    context = {
        "total_templates": data["total_templates"] or 0,
        "total_products": data["total_products"] or 0,
        "total_stocks": total_stocks,
       "total_users": users["total_users"],
        "total_merchants": users["total_merchants"],
        "total_clients": users["total_clients"],
        "total_employees": users["total_employees"],
      
    }
   


    return render(request, "dashboard/dashboard.html", context)