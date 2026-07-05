from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from functools import wraps

# 1) ✅ Simple user (no account_type set)
def simple_user_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = request.user
        if (
            user.is_authenticated and
            user.is_active and
            not user.is_staff and
            not user.is_superuser
        ):
            acct = getattr(user, "account_type", None)
            if acct in (None, "",):   # simple / legacy users
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden("Unauthorized account type")
        return redirect('/accounts/signin/')
    return wrapper


# 2) ✅ Client
def client_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = request.user
        if (
            user.is_authenticated and
            user.is_active and
            not user.is_staff and
            not user.is_superuser
        ):
            if getattr(user, "account_type", None) == "Client":
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden("Client account required")
        return redirect('/accounts/signin/')
    return wrapper


# 3) ✅ Merchant
def merchant_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = request.user
        if (
            user.is_authenticated and
            user.is_active and
            not user.is_staff and
            not user.is_superuser
        ):
            if getattr(user, "account_type", None) == "Merchant":
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden("Merchant account required")
        return redirect('/accounts/signin/')
    return wrapper


# 4) ✅ Employee
# if your Employees are ALSO staff, you can relax the "not user.is_staff" here
def employee_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = request.user
        if user.is_authenticated and user.is_active:
            # if employees are stored only via account_type
            if getattr(user, "account_type", None) == "Employee":
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden("Employee account required")
        return redirect('/accounts/signin/')
    return wrapper


# (optional) keep your staff/superadmin ones as they were
def staff_required(role=None):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated and request.user.is_staff:
                if role:
                    if getattr(request.user, 'role', None) == role:
                        return view_func(request, *args, **kwargs)
                    return HttpResponseForbidden("Unauthorized role")
                return view_func(request, *args, **kwargs)
            return redirect('/accounts/signin/')
        return wrapper
    return decorator


def superadmin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        return redirect('/accounts/signin/')
    return wrapper
