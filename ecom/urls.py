from django.urls import path
from . import views, shop, search
urlpatterns = [

    path('',views.Home, name="Home"),

    path("shop/search/", search.live_search, name="live_search"),
    path("user/", views.user_entry, name="user_entry"),
    path("review/submit/", views.submit_review, name="submit_review"),


    path('shop/', shop.Shop, name="shop"),
    path('shop/<slug:category_slug>/', shop.Shop, name="shop_category"),
    path('shop/<slug:category_slug>/<slug:subcategory_slug>/', shop.Shop, name="shop_subcategory"),




    path('shop-view/product/<str:prod_id>/',views.ProductView, name="ProductView"),
    path('about-us/',views.AboutUs, name="AboutUs"),
    path('contact-us/',views.ContactUs, name="ContactUs"),
    path('faq/',views.FAQ, name="FAQ"),
]
