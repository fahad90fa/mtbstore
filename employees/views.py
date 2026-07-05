from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from accounts.decorator import employee_required
from .models import EmployeeEntry
from decimal import Decimal
from accounts.models import CustomUser

@employee_required
def EmployeesHome(request):
    employee = request.user  # locked to logged-in employee

    customers = CustomUser.objects.filter(
        account_type__in=["Client", "Merchant"]
    )

    if request.method == "POST":
        EmployeeEntry.objects.create(
            employee=employee,
            date=request.POST.get("date"),
            entry_type=request.POST.get("entry_type"),
            customer_id=request.POST.get("customer_id") or None,
            title=request.POST.get("title"),
            details=request.POST.get("details"),
            total_amount=Decimal(request.POST.get("total_amount", "0"))
        )
        return redirect(request.path)

    entries = (
        EmployeeEntry.objects
        .filter(employee=employee)
        .order_by("-date", "-id")
    )

    return render(
        request,
        "employee/home.html",
        {
            "entries": entries,
            "customers": customers,
        }
    )