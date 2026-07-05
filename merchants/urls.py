from django.urls import path
from . import views
urlpatterns = [

    path('',views.MerchantsHome, name="MerchantsHome"),
]
