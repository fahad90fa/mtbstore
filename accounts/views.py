from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import CustomUser


def Signin(request):
    if request.method == 'POST':
        choice = request.POST.get('choice', '').strip()
        password = request.POST.get('password', '').strip()
        
        try:
            if choice == 'email':
                identifier = request.POST.get('email', '').strip().lower()
                user_obj = CustomUser.objects.get(email=identifier)
            elif choice == 'phone':
                identifier = request.POST.get('phone', '').strip()
                user_obj = CustomUser.objects.get(mobile_number=identifier)
            elif choice == 'cnic':
                identifier = request.POST.get('cnic', '').strip()
                user_obj = CustomUser.objects.get(cnic=identifier)
            else:
                return render(request, "accounts/pages/signin.html", {
                    "error": "Invalid login choice.",
                })
            
            user = authenticate(request, username=user_obj.username, password=password)

            if user:
                login(request, user)
                user.status = "Online"
                user.save()
                if user.is_superuser:
                    if request.headers.get("HX-Request"):
                        return HttpResponse(headers={"HX-Redirect": "/dashboard/"})
                    return redirect("/dashboard/")
                
                if user.account_type == "Client":
                    if request.headers.get("HX-Request"):
                        return HttpResponse(headers={"HX-Redirect": "/users/client/"})
                    return redirect("/users/client/")
            
                if user.account_type == "Merchant":
                    if request.headers.get("HX-Request"):
                        return HttpResponse(headers={"HX-Redirect": "/users/merchant/"})
                    return redirect("/users/merchant/")
            
                if user.account_type == "Employee":
                    if request.headers.get("HX-Request"):
                        return HttpResponse(headers={"HX-Redirect": "/users/employee/"})
                    return redirect("/users/employee/")
            else:
                return render(request, "accounts/pages/signin.html", {
                    "error": "Invalid password.",
                    "identifier": identifier
                })

        except CustomUser.DoesNotExist:
            return render(request, "accounts/pages/signin.html", {
                "error": f"User with this {choice} does not exist.",
                "identifier": identifier
            })

    return render(request, "accounts/pages/signin.html")


def Signup(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        User = CustomUser.objects.create_user(
            username=email,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
            user_pass=password,
            account_type="Client",
        )
        # user_obj = CustomUser.objects.get(email=email)
        authenticated_user = authenticate(request, username=email, password=password)
        if authenticated_user is not None:
            login(request, authenticated_user)
            return redirect('/users/client/')   
        else:
            return HttpResponse("Authentication failed after signup.", status=400)    
        

    return render(request, "accounts/pages/signup.html")



def check_email(request):
    email = request.POST.get("email", "").strip().lower()
    if not email:
        return HttpResponse(' ')

    if CustomUser.objects.filter(email=email).exists():
        return HttpResponse(
            '<div id="email-validation-msg" class="text-danger">'
            ''
            '<script>document.getElementById("email").setCustomValidity("Email already in use");</script>'
            '</div>'
        )
    else:
        return HttpResponse(
            '<div id="email-validation-msg" class="text-success">'
            ''
            '<script>document.getElementById("email").setCustomValidity("");</script>'
            '</div>'
        )
    

def Logout(request):
    user = request.user
    user.status = "Offline"
    user.save()
    logout(request)
    return redirect('/accounts/signin/')    