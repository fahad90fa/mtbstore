from django.shortcuts import render, HttpResponse
from accounts.decorator import merchant_required
from .models import Invoice
# Create your views here.
@merchant_required
def MerchantsHome(request):
    invoices = Invoice.objects.filter(merchant_id=request.user.mtb_id).order_by('-id').all()
    context = {
        "invoices": invoices,
    }
    return render(request, "merchant/home.html", context)

