from django.shortcuts import render, HttpResponse
from dashboard.models import Template,Category, SubCategory
from django.core.paginator import Paginator
from django.db.models import Prefetch

def Shop(request, category_slug=None, subcategory_slug=None, page_no=1):
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
    # Base queryset: ONLY products
    products = Template.objects.filter(
        type="product",
        status="active"
    ).prefetch_related(
        "category",
        "subcategory"
    )

    # Filter by category if present
    if category_slug:
        products = products.filter(
            category__slug=category_slug
        )

    # Filter by subcategory if present
    if subcategory_slug:
        products = products.filter(
            subcategory__slug=subcategory_slug
        )

    products = products.distinct()

    # Pagination
    per_page = int(request.GET.get("per_page", 12))
    paginator = Paginator(products, per_page)
    
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)


    context = {
        "all_templates": all_templates,
        "products": page_obj,
        "page_obj": page_obj,
        "category_slug": category_slug,
        "subcategory_slug": subcategory_slug,
        "per_page": per_page
    }

    return render(request, "ecom/shop.html", context)