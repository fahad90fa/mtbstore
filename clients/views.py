from django.shortcuts import render, HttpResponse
from accounts.decorator import client_required, simple_user_required
from merchants.models import Invoice
# Create your views here.
@client_required
def ClientsHome(request):
    invoices = Invoice.objects.filter(merchant_id=request.user.mtb_id).order_by('-id').all()
    context = {
        "invoices": invoices,
    }
    return render(request, "client/home.html", context)

