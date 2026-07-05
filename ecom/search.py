from django.http import JsonResponse
from django.db.models import Q
from dashboard.models import Template

def live_search(request):
    q = request.GET.get("q", "").strip()

    if not q:
        return JsonResponse([], safe=False)

    products = (
        Template.objects
        .filter(
            type="product",
            status="active"
        )
        .filter(
            Q(title__icontains=q) |
            Q(tags__icontains=q)
        )
        .prefetch_related("category")   # needed only for response display
        .distinct()
        [:8]
    )

    data = []
    for p in products:
        first_cat = p.category.first()
        data.append({
            "prod_id": p.prod_id,
            "title": p.title,
            "price": p.show_price,
            "img": p.img.url if p.img else "",
            "category": first_cat.title if first_cat else "",
            "category_slug": first_cat.slug if first_cat else "",
        })

    return JsonResponse(data, safe=False)
