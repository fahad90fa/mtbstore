from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from accounts.decorator import superadmin_required
from accounts.models import CustomUser
from .dry import generate_strong_password
from merchants.models import Invoice
from decimal import Decimal, InvalidOperation
from .models import Alert

# ───────────────────────────────

    # Merchants (Home)

# ───────────────────────────────

@superadmin_required
def MerchantHome(request):
    merchants = CustomUser.objects.filter(account_type="Merchant").all()
    content = {
        'merchants': merchants,
    }
    return render(request, "dashboard/merchants.html", content)

@superadmin_required
def AddMerchant(request):
    if request.method == 'POST':
        password = generate_strong_password()
        User = CustomUser.objects.create(
            username=request.POST.get("email"),
            email=request.POST.get("email"),
            profile_pic = request.FILES.get('profile_pic'),
            account_type = "Merchant",
            first_name=request.POST.get("display_name"),
            user_pass=password,
        )
        User.set_password(password)
        User.save()
    return redirect(request.META.get('HTTP_REFERER', '/'))    


@superadmin_required
def DeleteMerchant(request, merchant_id):
    merchant = get_object_or_404(CustomUser, id=merchant_id)

    raw_balance = merchant.merchant_balance or "0"

    try:
        balance = Decimal(str(raw_balance))
    except InvalidOperation:
        balance = Decimal("0")

    if balance < 1:
        merchant.delete()

    return redirect(request.META.get('HTTP_REFERER', '/'))



@superadmin_required
def ViewMerchant(request, mtb_id):
    invoices = Invoice.objects.filter(merchant_id=mtb_id).order_by('-id')

    merchant = CustomUser.objects.filter(mtb_id=mtb_id).first()
    content = {
        'invoices': invoices,
        'merchant':merchant
    }
    return render(request, "dashboard/merchantsPages/viewMerchant.html", content)


@superadmin_required
def SettingsMerchant(request, mtb_id):
    invoices = Invoice.objects.filter(merchant_id=mtb_id).all()
    merchant = CustomUser.objects.filter(mtb_id=mtb_id).first()
    if request.method == 'POST':
        merchant.first_name = request.POST.get("fname")
        merchant.last_name = request.POST.get("lname")
        merchant.address = request.POST.get("address")
        merchant.email = request.POST.get("email")
        merchant.mobile_number = request.POST.get("phone")
        merchant.cnic = request.POST.get("cnic")
        profile_pic = request.FILES.get('avatar')
        if profile_pic:
            merchant.profile_pic = profile_pic
        merchant.save()
        return redirect(request.META.get('HTTP_REFERER', '/'))
    content = {
        'invoices': invoices,
        'merchant':merchant
    }
    return render(request, "dashboard/merchantsPages/settingsMerchant.html", content)

@superadmin_required
def AlertsMerchant(request, mtb_id):
    alerts = Alert.objects.filter(mtb_id=mtb_id).order_by('-datetime').all()
    merchant = CustomUser.objects.filter(mtb_id=mtb_id).first()
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
        'merchant':merchant
    }
    return render(request, "dashboard/merchantsPages/alertsMerchant.html", content)


@superadmin_required
def PrintLedger(request, mtb_id):
    invoices = Invoice.objects.filter(merchant_id=mtb_id).all()
    merchant = CustomUser.objects.filter(mtb_id=mtb_id).first()
    content = {
        'invoices': invoices,
        'merchant':merchant
    }
    return render(request, "invoices/printLedger.html", content)


@superadmin_required
def AddCreditMerchant(request, mtb_id):
    if request.method == 'POST':
        credit=request.POST.get("credit")
        date=request.POST.get("date")
        payment_method=request.POST.get("payment_method")
        payment_reference=request.POST.get("payment_reference")
        payment_to=request.POST.get("payment_to")
        merchant = CustomUser.objects.filter(mtb_id=mtb_id).first()
        merchant.merchant_balance = Decimal(merchant.merchant_balance) - Decimal(credit)
        merchant.save()
        Invoice.objects.create(
            merchant_id = mtb_id,
            credit = credit,
            balance = merchant.merchant_balance,
            date = date,
            source_type = "Payment",
            payment_method = payment_method,
            payment_reference = payment_reference,
            payment_to = payment_to
        )
    
    return redirect(request.META.get('HTTP_REFERER', '/'))    
