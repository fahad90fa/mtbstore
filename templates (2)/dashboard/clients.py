from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from accounts.decorator import superadmin_required
from accounts.models import CustomUser
from dashboard.models import Alert
from decimal import Decimal
from merchants.models import Invoice
from .dry import generate_strong_password

# ───────────────────────────────

    # Clients (Home)

# ───────────────────────────────

@superadmin_required
def ClientHome(request):
    clients = CustomUser.objects.filter(account_type="Client").all()
    content = {
        'clients': clients,
    }
    return render(request, "dashboard/clients.html", content)

@superadmin_required
def AddClient(request):
    if request.method == 'POST':
        password = generate_strong_password()
        User = CustomUser.objects.create(
            username=request.POST.get("email"),
            email=request.POST.get("email"),
            profile_pic = request.FILES.get('profile_pic'),
            account_type = "Client",
            first_name=request.POST.get("display_name"),
            user_pass=password,
        )
        User.set_password(password)
        User.save()
    return redirect(request.META.get('HTTP_REFERER', '/'))    


@superadmin_required
def DeleteClient(request, client_id):
    client = get_object_or_404(CustomUser, id=client_id)
    client.delete()
    return redirect(request.META.get('HTTP_REFERER', '/'))


@superadmin_required
def ViewClient(request, mtb_id):
    invoices = (
        Invoice.objects
        .filter(
            merchant_id=mtb_id,
            source_type__in=["ClientInvoice", "Payment"]
        ).all())
    client = CustomUser.objects.filter(mtb_id=mtb_id).first()
    content = {
        'client':client,
        'invoices': invoices,
    }
    return render(request, "dashboard/clientsPages/viewClient.html", content)

@superadmin_required
def SettingsClient(request, mtb_id):
    client = CustomUser.objects.filter(mtb_id=mtb_id).first()
    if request.method == 'POST':
        client.first_name = request.POST.get("fname")
        client.last_name = request.POST.get("lname")
        client.address = request.POST.get("address")
        client.email = request.POST.get("email")
        client.mobile_number = request.POST.get("phone")
        client.cnic = request.POST.get("cnic")
        profile_pic = request.FILES.get('avatar')
        if profile_pic:
            client.profile_pic = profile_pic
        client.save()
        return redirect(request.META.get('HTTP_REFERER', '/'))
    content = {
        'client': client
    }
    return render(request, "dashboard/clientsPages/settingsClient.html", content)

@superadmin_required
def AlertsClient(request, mtb_id):
    alerts = Alert.objects.filter(mtb_id=mtb_id).order_by('-datetime').all()
    client = CustomUser.objects.filter(mtb_id=mtb_id).first()
    if request.method == 'POST':
        text = request.POST.get("text")
        expiration_datetime = request.POST.get("expiration_datetime")
        Alert.objects.create(
            mtb_id = mtb_id,
            text = text,
            expiration_datetime = expiration_datetime
        )
        return redirect(request.META.get('HTTP_REFERER', '/'))
    content = {
        'alerts': alerts,
        'client':client
    }
    return render(request, "dashboard/clientsPages/alertsClient.html", content)


@superadmin_required
def AddCreditClient(request, mtb_id):
    if request.method == "POST":
        credit = request.POST.get("credit")
        date = request.POST.get("date")
        payment_method = request.POST.get("payment_method")
        payment_reference = request.POST.get("payment_reference")
        payment_to = request.POST.get("payment_to")

        client = CustomUser.objects.filter(
            mtb_id=mtb_id,
            account_type="Client"
        ).first()

        # update client balance
        client.client_balance = Decimal(client.client_balance) - Decimal(credit)
        client.save()

        # create invoice entry
        Invoice.objects.create(
            merchant_id=mtb_id,
            credit=credit,
            balance=client.client_balance,
            date=date,
            source_type="Payment",
            payment_method=payment_method,
            payment_reference=payment_reference,
            payment_to=payment_to
        )

    return redirect(request.META.get("HTTP_REFERER", "/"))