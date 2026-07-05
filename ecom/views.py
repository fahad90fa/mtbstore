from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from dashboard.models import Template,Category, SubCategory, ProductReview
from django.http import JsonResponse
from django.db.models import Avg
from .models import ContactMessage









def Home(request):
    all_templates = (
        Template.objects
        .filter(type="template")
        .prefetch_related(
            Prefetch(
                "category",
                queryset=Category.objects.filter(status="active")
                .prefetch_related("subcategories")
            )
        )
    )
    categories = (
        Category.objects
        .filter(status="active")
        .prefetch_related("subcategories")
    )
    new_products = (
        Template.objects
        .filter(type="product", status="active")
        .order_by("-created_at")[:7]
    )

    exclude_ids = new_products.values_list("id", flat=True)

    # Random products, excluding first 7
    deal_products = (
        Template.objects
        .filter(type="product", status="active")
        .exclude(id__in=exclude_ids)
        .order_by("?")[:7]
    )
    content = {
        'all_templates': all_templates,
        'categories': categories,
        'new_products': new_products,
        'deal_products': deal_products,
    }
    return render(request, "ecom/home.html", content)




def ProductView(request, prod_id):
    # Sidebar templates (unchanged, but correct)
    all_templates = (
        Template.objects
        .filter(type="template")
        .prefetch_related(
            Prefetch(
                "category",
                queryset=Category.objects.filter(status="active")
                .prefetch_related("subcategories")
            )
        )
    )

    # ---- Selected product ----
    product = get_object_or_404(
        Template,
        prod_id=prod_id,
        type="product",
        status="active"
    )

    

    # ---- Approved reviews only ----
    approved_reviews = (
        product.reviews
        .filter(is_approved=True)
        .order_by("-created_at")
    )
    avg_rating = approved_reviews.aggregate(
        avg=Avg("rating")
    )["avg"]
    avg_rating = round(avg_rating) if avg_rating else 0
    total_reviews = approved_reviews.count()

    # ---- Base queryset for related products ----
    base_qs = (
        Template.objects
        .filter(type="product", status="active")
        .exclude(id=product.id)
    )

    related_products = []

    # ---- 1️⃣ Priority: title OR tags ----
    if product.title or product.tags:
        title_tags_q = Q()
        if product.title:
            title_tags_q |= Q(title__icontains=product.title)
        if product.tags:
            title_tags_q |= Q(tags__icontains=product.tags)

        related_products = list(
            base_qs.filter(title_tags_q)
            .distinct()[:4]
        )

    # ---- 2️⃣ Fallback: same category ----
    if len(related_products) < 4:
        category_ids = product.category.values_list("id", flat=True)

        category_matches = (
            base_qs
            .filter(category__id__in=category_ids)
            .exclude(id__in=[p.id for p in related_products])
            .distinct()[: 4 - len(related_products)]
        )

        related_products.extend(category_matches)

    # ---- 3️⃣ Final fallback: most recent ----
    if len(related_products) < 4:
        recent_fallback = (
            base_qs
            .exclude(id__in=[p.id for p in related_products])
            .order_by("-created_at")[: 4 - len(related_products)]
        )

        related_products.extend(recent_fallback)

    context = {
        "all_templates": all_templates,
        "product": product,
        "related_products": related_products,
        "approved_reviews": approved_reviews,
        "avg_rating": avg_rating,
        "total_reviews": total_reviews,
    }

    return render(request, "ecom/productView.html", context)


def submit_review(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    product = get_object_or_404(
        Template,
        prod_id=request.POST.get("product_id"),
        type="product",
        status="active"
    )

    rating = int(request.POST.get("rating", 0))
    if rating < 1 or rating > 5:
        return JsonResponse({"error": "Invalid rating"}, status=400)

    ProductReview.objects.create(
        product=product,
        user=request.user if request.user.is_authenticated else None,
        name=request.POST.get("name", "").strip(),
        email=request.POST.get("email", "").strip(),
        rating=rating,
        comment=request.POST.get("comment", "").strip(),
    )

    return JsonResponse({"success": True})
def AboutUs(request):
    all_templates = (
        Template.objects
        .filter(type="template")
        .prefetch_related(
            Prefetch(
                "category",
                queryset=Category.objects.filter(status="active")
                .prefetch_related("subcategories")
            )
        )
    )
    content = {
        'all_templates': all_templates,
    }
    return render(request, "ecom/aboutUs.html", content)




def ContactUs(request):
    all_templates = (
        Template.objects
        .filter(type="template")
        .prefetch_related(
            Prefetch(
                "category",
                queryset=Category.objects.filter(status="active")
                .prefetch_related("subcategories")
            )
        )
    )

    success = False
    errors = {}

    if request.method == "POST":
        full_name = (request.POST.get("fname") or "").strip()
        email = (request.POST.get("umail") or "").strip()
        phone = (request.POST.get("phone") or "").strip()
        message = (request.POST.get("message") or "").strip()

        if not full_name:
            errors["fname"] = "Full name is required"
        if not email:
            errors["umail"] = "Email is required"
        if not message:
            errors["message"] = "Message is required"

        if not errors:
            ContactMessage.objects.create(
                full_name=full_name,
                email=email,
                phone=phone,
                message=message,
            )
            success = True

    content = {
        'all_templates': all_templates,
        'success': success,
        'errors': errors,
    }
    return render(request, "ecom/contactUs.html", content)




def FAQ(request):
    all_templates = (
        Template.objects
        .filter(type="template")
        .prefetch_related(
            Prefetch(
                "category",
                queryset=Category.objects.filter(status="active")
                .prefetch_related("subcategories")
            )
        )
    )
    content = {
        'all_templates': all_templates,
    }
    return render(request, "ecom/faq.html", content)



@login_required(login_url="/accounts/signin/")
def user_entry(request):
    user = request.user

    # Superuser / Admin
    if user.is_superuser:
        if request.headers.get("HX-Request"):
            return HttpResponse(headers={"HX-Redirect": "/dashboard/"})
        return redirect("/dashboard/")

    # Client
    if user.account_type == "Client":
        if request.headers.get("HX-Request"):
            return HttpResponse(headers={"HX-Redirect": "/users/client/"})
        return redirect("/users/client/")

    # Merchant
    if user.account_type == "Merchant":
        if request.headers.get("HX-Request"):
            return HttpResponse(headers={"HX-Redirect": "/users/merchant/"})
        return redirect("/users/merchant/")

    # Employee
    if user.account_type == "Employee":
        if request.headers.get("HX-Request"):
            return HttpResponse(headers={"HX-Redirect": "/users/employee/"})
        return redirect("/users/employee/")

    # Fallback (should never happen, but safe)
    if request.headers.get("HX-Request"):
        return HttpResponse(headers={"HX-Redirect": "/"})
    return redirect("/")