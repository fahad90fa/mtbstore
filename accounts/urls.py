from django.urls import path
from . import views
urlpatterns = [

    path('signin/',views.Signin, name="Signin"),
    path('signup/',views.Signup, name="Signup"),
    path('logout/',views.Logout, name="Logout"),

    path("check-email/", views.check_email, name="check_email"),
    # path('signupSteps/<int:step>/', views.signupSteps, name="signupSteps"),
    # # urls.py
    # path("check-email/", views.check_email, name="check_email"),

    # path('logout/', views.Logout, name='LogoutPage'),

]
