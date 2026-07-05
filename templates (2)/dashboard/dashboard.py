from django.forms import IntegerField
from django.shortcuts import render, HttpResponse, get_object_or_404, redirect
from accounts.decorator import superadmin_required
from django.views.decorators.http import require_POST
from django.utils.timezone import now
from .models import Alert, DraftInvoice, Template
from django.http import JsonResponse
from ecom.models import ContactMessage
from django.db.models import Count
from django.db.models.functions import Cast
from django.utils import timezone
from datetime import timedelta



from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta

@superadmin_required
def Dashboard(request):
   

    context = {
       
    }

    return render(request, "dashboard/dashboard.html", context)