from django.urls import path
from . import views
urlpatterns = [

    path('',views.EmployeesHome, name="EmployeesHome"),
]
