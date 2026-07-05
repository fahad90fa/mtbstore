from decimal import Decimal
from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from accounts.decorator import superadmin_required
from accounts.models import CustomUser
from employees.models import EmployeeEntry
from .dry import generate_strong_password

# ───────────────────────────────

    # Merchants (Home)

# ───────────────────────────────

@superadmin_required
def EmployeeHome(request):
    employees = CustomUser.objects.filter(account_type="Employee").all()
    content = {
        'employees': employees,
    }
    return render(request, "dashboard/employees.html", content)

@superadmin_required
def AddEmployee(request):
    if request.method == 'POST':
        password = generate_strong_password()
        User = CustomUser.objects.create(
            username=request.POST.get("email"),
            email=request.POST.get("email"),
            profile_pic = request.FILES.get('profile_pic'),
            account_type = "Employee",
            first_name=request.POST.get("display_name"),
            user_pass=password,
        )
        User.set_password(password)
        User.save()
    return redirect(request.META.get('HTTP_REFERER', '/'))    


@superadmin_required
def DeleteEmployee(request, employee_id):
    employee = get_object_or_404(CustomUser, id=employee_id)
    employee.delete()
    return redirect(request.META.get('HTTP_REFERER', '/'))



@superadmin_required
def ViewEmployee(request, mtb_id):
    employee = get_object_or_404(
        CustomUser,
        mtb_id=mtb_id,
        account_type="Employee"
    )

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
        .order_by("date", "id")
    )

    return render(
        request,
        "dashboard/employeesPages/viewEmployee.html",
        {
            "employee": employee,
            "entries": entries,
            "customers": customers,
        }
    )

@superadmin_required
def delete_employee_entry(request, entry_id):
    entry = get_object_or_404(EmployeeEntry, id=entry_id)
    entry.delete()
    return redirect(request.META.get("HTTP_REFERER", "/"))

@superadmin_required
def SettingsEmployee(request, mtb_id):
    employee = CustomUser.objects.filter(mtb_id=mtb_id).first()
    if request.method == 'POST':
        employee.first_name = request.POST.get("fname")
        employee.last_name = request.POST.get("lname")
        employee.address = request.POST.get("address")
        employee.email = request.POST.get("email")
        employee.mobile_number = request.POST.get("phone")
        employee.cnic = request.POST.get("cnic")
        employee.salary = request.POST.get("salary")
        profile_pic = request.FILES.get('avatar')
        if profile_pic:
            employee.profile_pic = profile_pic
        employee.save()
        return redirect(request.META.get('HTTP_REFERER', '/'))
    content = {
        'employee': employee
    }
    return render(request, "dashboard/employeesPages/settingsEmployee.html", content)