from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from accounts.decorator import superadmin_required
from .models import Template, CustomField, Stock, Category, SubCategory, AdvancedFilterSettings, ProductReview
from django.http import HttpResponseBadRequest, JsonResponse
import json
from datetime import datetime
from accounts.models import CustomUser
from merchants.models import Invoice, InvoiceItem
from decimal import ROUND_HALF_UP, Decimal
from django.views.decorators.http import require_POST
from django.db import transaction
from collections import defaultdict
from django.db.models import Avg, Count, Q, F
from django.db.models.functions import Coalesce, Round
from django.db.models import IntegerField

# ───────────────────────────────

    # Inventory (Major Search)

# ───────────────────────────────

@superadmin_required
def InventoryHome(request):
    settings = AdvancedFilterSettings.get_solo()
    filters = settings.filters
    products = (
    Template.objects
    .filter(type="product")
    .annotate(
        avg_rating=Coalesce(
            Avg("reviews__rating", filter=Q(reviews__is_approved=True)),
            0.0
        ),
        avg_rating_int=Coalesce(
            Round(Avg("reviews__rating", filter=Q(reviews__is_approved=True))),
            0,
            output_field=IntegerField()
        ),
        rating_count=Count(
            "reviews",
            filter=Q(reviews__is_approved=True)
        )
    )
     .order_by("-created_at")
)

    all_templates = Template.objects.filter(type="template").prefetch_related(
        "category__subcategories"
    )

    all_products = (
    Template.objects
    .filter(type="product")
    .annotate(
        avg_rating=Coalesce(
            Avg("reviews__rating", filter=Q(reviews__is_approved=True)),
            0.0
        ),
        avg_rating_int=Coalesce(
            Round(
                Avg("reviews__rating", filter=Q(reviews__is_approved=True))
            ),
            0,
            output_field=IntegerField()
        ),
        rating_count=Count(
            "reviews",
            filter=Q(reviews__is_approved=True)
        )
    )
    .prefetch_related("category", "subcategory")
)

    # Build fast lookup maps
    cat_count = defaultdict(int)
    sub_count = defaultdict(int)
    cat_only_products = defaultdict(list)
    sub_products = defaultdict(list)

    for p in all_products:
        p_cats = list(p.category.all())
        p_subs = list(p.subcategory.all())

        # Count per category
        for c in p_cats:
            cat_count[c.cat_id] += 1

        # Count per subcategory + list products under subcat
        for s in p_subs:
            sub_count[s.subcat_id] += 1
            sub_products[s.subcat_id].append(p)

        # Category-only products (no subcategories)
        if len(p_subs) == 0:
            for c in p_cats:
                cat_only_products[c.cat_id].append(p)

    # Attach computed attributes to category/subcategory objects so template can read them
    for t in all_templates:
        for c in t.category.all():
            c.product_count = cat_count[c.cat_id]
            c.only_products = cat_only_products[c.cat_id]
            for s in c.subcategories.all():
                s.product_count = sub_count[s.subcat_id]
                s.products = sub_products[s.subcat_id]
    context = {
        "filters": filters,
        "products":products,
        "all_templates":all_templates,
        "all_products": all_products
    }

    return render(request, "dashboard/inventory.html", context)



@superadmin_required
def AdvancedSearchFilter(request):
    if request.method == 'POST':
        data = {
            "filter": request.POST.get("filter"),
        }

        # Save to singleton model
        settings = AdvancedFilterSettings.get_solo()
        settings.filters = data
        settings.save()

    return redirect("/inventory/")








# ───────────────────────────────

    # Category, Subcategory

# ───────────────────────────────



@superadmin_required
def Categories(request):
    categories = Category.objects.all()
    return render(request, "dashboard/inventoryPages/categories.html", {'categories':categories})


@superadmin_required
def AddCategory(request):
    if request.method == 'POST':
        tem_id=request.POST.get("tem_id")
        category  = Category.objects.create(
            title=request.POST.get("title"),
            tem_id=tem_id,
            img = request.FILES.get('img'),
            status=request.POST.get("status"),
            description=request.POST.get("description"))
        temp = Template.objects.filter(tem_id=tem_id).first()
        temp.category.add(category)
        temp.total_category = str(int(temp.total_category) + 1)
        temp.save()
    return redirect(request.META.get('HTTP_REFERER', '/'))    




@superadmin_required
def AddSubcategory(request):
    if request.method == 'POST':
        category=request.POST.get("category")
        category = get_object_or_404(Category, cat_id=category)
        subcategory = SubCategory.objects.create(
            title=request.POST.get("title"),
            category=category,
            description=request.POST.get("description"))
        temp = Template.objects.filter(tem_id=category.tem_id).first()
        temp.subcategory.add(subcategory)
        temp.total_subcategory = str(int(temp.total_subcategory) + 1)
        temp.save()
    return redirect(request.META.get('HTTP_REFERER', '/'))    



@superadmin_required
def DeleteCategory(request, cat_id):
    category = get_object_or_404(Category, cat_id=cat_id)

    try:
        # Count subcategories related to this category
        total_subcategories = category.subcategories.count()

        # Count "product" type templates using this category
        total_products = Template.objects.filter(category=category, type='product').count()

        if total_subcategories > 0 or total_products > 0:
            return HttpResponseBadRequest(
                f"Cannot delete category '{category.title}' because it has related data. "
                f"(Subcategories: {total_subcategories}, Products: {total_products})"
            )

    except Exception as e:
        return HttpResponseBadRequest(f"Error checking related data: {str(e)}")
    if category.img:
            category.img.delete(save=False)
    category.delete()
    temp = Template.objects.filter(tem_id=category.tem_id).first()
    temp.total_category = str(int(temp.total_category) - 1)
    temp.save()
    return redirect(request.META.get('HTTP_REFERER', '/'))    

@superadmin_required
def DeleteSubcategory(request, subcat_id):
    subcat = get_object_or_404(SubCategory, subcat_id=subcat_id)
    subcat.delete()
    temp = Template.objects.filter(tem_id=subcat.category.tem_id).first()
    temp.total_subcategory = str(int(temp.total_subcategory) - 1)
    temp.save()
    return redirect(request.META.get('HTTP_REFERER', '/'))



@superadmin_required
def EditCategory(request, cat_id):
    category = Category.objects.filter(cat_id=cat_id).first()
    subcategories = category.subcategories.all()
    categories = Category.objects.all()
    if request.method == 'POST':
        category.title = request.POST.get("title")
        category.description = request.POST.get("description")
        category.status = request.POST.get("status")

        if request.FILES.get('img'):
            category.img = request.FILES['img']
        category.save()
        
    content = {
        'cat_id':cat_id,
        'category': category,
        'subcategories': subcategories,
        'categories':categories
    }
    return render(request, "dashboard/inventoryPages/editCategory.html", content)






# ───────────────────────────────

    # Stock

# ───────────────────────────────


@superadmin_required
def Stocks(request):
    stocks = Stock.objects.all()
    return render(request, "dashboard/inventoryPages/stocks.html", {'stocks':stocks})



@superadmin_required
def AddStock(request):
    merchants = CustomUser.objects.filter(account_type="Merchant").all()
    templates = Template.objects.filter(type='template')
    invoice_id = None
    if request.method == 'POST':
        # Stock
        name = request.POST.get("name")
        date = request.POST.get("date")
        color = request.POST.get("color")
        details = request.POST.get("details")
        total_amount = request.POST.get("total_amount")
        stock_source = request.POST.get("stock_source")
        stock_location = request.POST.get("stock_location")
        stock_handler = request.POST.get("stock_handler")
        merchant_mtb_id = request.POST.get("merchant_mtb_id")
        stock_obj = Stock.objects.create(
            name=name,
            color = color,
            details=details,
            mtb_id=merchant_mtb_id)
        # Merchant
        # some payment calculation ----------------------------
        merchant = CustomUser.objects.filter(mtb_id=merchant_mtb_id).first()
        merchant.merchant_balance = (Decimal(merchant.merchant_balance)+ Decimal(total_amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        merchant.save()


        # Products
        products_json = request.POST.get("stock_products_json", "[]")
        try:
            products = json.loads(products_json)
            print("come in post try")
        except json.JSONDecodeError:
            print("come in post except")
            products = []

        # Adding Invoice content here 
        new_invoice = Invoice.objects.create(
            stock_id = stock_obj.stock_id,
            merchant_id = merchant_mtb_id,
            total = total_amount,
            debit = total_amount,
            credit = "0",
            balance = merchant.merchant_balance,
            source_type = "Stock",
            stock_source = stock_source,
            stock_location = stock_location,
            stock_handler = stock_handler,
            date = date
        )
        invoice_id = new_invoice.invoice_id
        for item in products:
            template_id = item.get("template_id")
            name = item.get("name")
            qty = item.get("qty") or 0
            rate = item.get("rate") or 0
            amount = item.get("amount") or 0
            base_price_pre = item.get("base_price") or 0
            base_price_percentage = item.get("percentage_value") or 0
            base_price_percentage_sign = item.get("percentage_type") or 0
            base_price = item.get("retail_price") or 0

            # Add product count to template & stock
            temp = Template.objects.get(tem_id=template_id, type="template")
            temp.total_product = str(int(temp.total_product) + int(qty))
            temp.save()
            stock_obj.total_products = str(int(stock_obj.total_products) + int(qty))
            stock_obj.invested = (
            Decimal(stock_obj.invested) + Decimal(amount)).quantize(Decimal("0.00"), rounding=ROUND_HALF_UP)

            stock_obj.save()


            # this is the important part: create a **draft** product
            # we don't have full data like your other screen, so we set minimal fields
            product = Template.objects.create(
                tem_id=template_id,           # or store as FK/ref if needed
                title=name,
                status="draft",               # <---- mark draft
                base_price=rate,
                available_product =qty,
                stock_product=qty,
                stock=stock_obj,
                type="product",
                base_price_pre = base_price_pre,
                base_price_percentage = base_price_percentage,
                base_price_percentage_sign = base_price_percentage_sign,
                created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                updated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
              # ⬅️ GET THE AUTO GENERATED PRODUCT ID HERE
            prod_id = product.prod_id 
            InvoiceItem.objects.create(
                invoice = new_invoice,
                product_name = name,
                rate = rate,
                quantity = qty,
                amount = amount,
                product_code = prod_id
            )

            # if you want to clone custom fields from the original template:
            try:
                current_template = Template.objects.get(tem_id=template_id, type="template")
                for field in current_template.custom_fields.all():
                    new_field = CustomField.objects.create(
                        field_name=field.field_name,
                        field_type=field.field_type,
                        is_required=field.is_required,
                        default_value=field.default_value
                    )
                    product.custom_fields.add(new_field)
            except Template.DoesNotExist:
                pass

    content = {
        'merchants':merchants,
        'templates': templates,
        'invoice_id':invoice_id
    }    
    return render(request, "dashboard/inventoryPages/addStocks.html",content)


@superadmin_required
def PrintInvoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, invoice_id=invoice_id)
    items = invoice.items.all()
    merchant = CustomUser.objects.filter(mtb_id=invoice.merchant_id).first()


    context = {
        "invoice": invoice,
        "items": items,
        "merchant":merchant
    }

    return render(request, "invoices/stock_invoice.html", context)



@superadmin_required
def DeleteCredit(request, invoice_id):
    invoice = get_object_or_404(Invoice, invoice_id=invoice_id)
    merchant = get_object_or_404(CustomUser, mtb_id=invoice.merchant_id)

    credit_amount = Decimal(invoice.credit or "0")

    with transaction.atomic():
        # reverse the balance effect
        merchant.merchant_balance = (
            Decimal(merchant.merchant_balance) + credit_amount
        )
        merchant.save()

        # delete the invoice
        invoice.delete()

    return redirect(request.META.get("HTTP_REFERER", "/"))


@superadmin_required
def DeleteStock(request, stock_id):
    stock = get_object_or_404(Stock, stock_id=stock_id)
    
    # Check if stock has associated products
    try:
        total_products = int(stock.total_products or 0)
        
        if total_products > 0:
            error_message = (
                "Cannot delete this stock because it contains product data. "
                "Deleting it would break the inventory consistency. "
                f"(Total Products: {total_products})"
            )
            return HttpResponseBadRequest(error_message)

    except (ValueError, TypeError):
        return HttpResponseBadRequest("Invalid data format in stock record")

    # If checks pass, delete the stock
    stock.delete()
    
    return redirect("/inventory/stocks/")






# ───────────────────────────────

    # Templates

# ───────────────────────────────



@superadmin_required
def Templates(request):
    templates = Template.objects.filter(type='template')
    return render(request, "dashboard/inventoryPages/templates.html", {'templates':templates})




@superadmin_required
def AddTemplate(request):
    if request.method == 'POST':
        template_name = request.POST.get("template_name")
        color = request.POST.get("color")
        field_name = request.POST.getlist('field_name[]')
        field_type = request.POST.getlist('field_type[]')
        is_required = request.POST.getlist('is_required[]')
        default_value = request.POST.getlist('default_value[]')

        add_template = Template.objects.create(
            type="template",
            template_name = template_name,
            color = color,)
        keyvalue = 0
        keyvalue_required = 0
        for a, b, c, d in zip(field_name, field_type, is_required, default_value):
            keyvalue = keyvalue+1
            if c == "True":
                keyvalue_required = keyvalue_required + 1
            custom_field = CustomField.objects.create(
            field_name=a,
            field_type=b,
            is_required=c,
            default_value=d)
            add_template.custom_fields.add(custom_field)
        add_template.keyvalue = keyvalue
        add_template.keyvalue_required = keyvalue_required
        add_template.save()
    
    return redirect("/inventory/templates/")



@superadmin_required
def DeleteTemplate(request, tem_id):
    template = get_object_or_404(Template, tem_id=tem_id)
    
    # Check if template has associated data
    try:
        total_product = int(template.total_product or 0)
        total_stock = int(template.total_stock or 0)
        total_category = int(template.total_category or 0)
        
        if any([total_product > 0, total_stock > 0, total_category > 0]):
            error_message = (
                "Cannot delete this template because it contains inventory data. "
                "Deleting it would crash the inventory system. "
                f"(Products: {total_product}, Stock: {total_stock}, Categories: {total_category})"
            )
            return HttpResponseBadRequest(error_message)
            
    except (ValueError, TypeError):
        # Handle case where values aren't proper numbers
        return HttpResponseBadRequest("Invalid data format in template records")
    
    # If checks pass, proceed with deletion
    template.custom_fields.all().delete()  # Delete related custom fields
    template.delete()
    
    return redirect("/inventory/templates/")






# ───────────────────────────────

    # Products

# ───────────────────────────────



@superadmin_required
def AddProduct(request, tem_id):
    product_added = False
    new_product_url = ""

    categories = Category.objects.all()
    templates = Template.objects.filter(type="template")
    stocks = Stock.objects.all()
    current_template = Template.objects.filter(tem_id=tem_id).first()

    if request.method == 'POST':
        category_ids = request.POST.getlist("category") 
        subcategory_ids = request.POST.getlist("subcategory")
        stock_id = request.POST.get("stock")

        title = request.POST.get("title")
        description = request.POST.get("description")
        img = request.FILES.get('img')
        status = request.POST.get("status")

        base_price_pre = request.POST.get("base_price_pre")
        base_price_percentage = request.POST.get("base_price_percentage")
        base_price_percentage_sign = request.POST.get("percentage")
        base_price = request.POST.get("base_price")
        show_price = request.POST.get("show_price")

        available_product = request.POST.get("available_product")
        stock_product = request.POST.get("stock_product")

        raw_tags = request.POST.get("tags", "[]")
        try:
            tags_list = json.loads(raw_tags)
            tags = ",".join([t["value"] for t in tags_list])
        except (json.JSONDecodeError, TypeError, KeyError):
            tags = ""

        # Create new product (still using Template model, but type is 'product')
        product = Template.objects.create(
            tem_id=tem_id,
            title=title,
            description=description,
            img=img,
            status=status,
            base_price_pre=base_price_pre,
            base_price_percentage=base_price_percentage,
            base_price_percentage_sign=base_price_percentage_sign,
            base_price=base_price,
            show_price=show_price,
            available_product=available_product,
            stock_product=stock_product,
            tags=tags,
            stock=Stock.objects.filter(stock_id=stock_id).first(),
            type="product",
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            updated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        if category_ids:
            product.category.set(category_ids)
        if subcategory_ids:
            product.subcategory.set(subcategory_ids)

        # ❗️Duplicate each CustomField from the template
        for field in current_template.custom_fields.all():
            field_key = f"custom_{field.id}"
            value = request.POST.get(field_key)

            new_field = CustomField.objects.create(
                field_name=field.field_name,
                field_type=field.field_type,
                is_required=field.is_required,
                default_value=value or field.default_value
            )
            product.custom_fields.add(new_field)

        product.save()
        product_added = True
        new_product_url = f"/inventory/edit-product/{product.prod_id}/"

    content = {
        'current_template': current_template,
        'tem_id': tem_id,
        'categories': categories,
        'templates': templates,
        'stocks': stocks,
        'product_added':product_added,
        'new_product_url':new_product_url
    }
    return render(request, "dashboard/inventoryPages/addProduct.html", content)


@superadmin_required
def EditProduct(request, prod_id):
    categories = Category.objects.all()
    templates = Template.objects.filter(type="template")
    stocks = Stock.objects.all()

    current_product = Template.objects.filter(prod_id=prod_id).first()
    if not current_product:
        return redirect("error_404")  # Optional: handle non-existent product gracefully

    current_template = Template.objects.filter(tem_id=current_product.tem_id, type="template").first()
    selected_subcats = list(current_product.subcategory.values_list('subcat_id', flat=True))

    
    approved_reviews = current_product.reviews.filter(is_approved=True)
    avg_rating = approved_reviews.aggregate(
        avg=Avg("rating")
    )["avg"]

    avg_rating = round(avg_rating) if avg_rating else 0

    if request.method == 'POST':
        category_ids = request.POST.getlist("category") 
        subcategory_ids = request.POST.getlist("subcategory")
        stock_id = request.POST.get("stock")

        current_product.title = request.POST.get("title")
        current_product.description = request.POST.get("description")
        current_product.status = request.POST.get("status")
        current_product.base_price_pre = request.POST.get("base_price_pre")
        current_product.base_price_percentage = request.POST.get("base_price_percentage")
        current_product.base_price_percentage_sign = request.POST.get("percentage")
        current_product.base_price = request.POST.get("base_price")
        current_product.show_price = request.POST.get("show_price")
        current_product.available_product = request.POST.get("available_product")
        current_product.stock_product = request.POST.get("stock_product")
        raw_tags = request.POST.get("tags", "[]")
        try:
            tags_list = json.loads(raw_tags)
            current_product.tags = ",".join([t["value"] for t in tags_list])
        except (json.JSONDecodeError, TypeError, KeyError):
            current_product.tags = ""
        current_product.stock = Stock.objects.filter(stock_id=stock_id).first()
        current_product.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Only update image if a new one is uploaded
        if request.FILES.get("img"):
            current_product.img = request.FILES.get("img")

        # Update many-to-many fields
        current_product.category.set(category_ids)
        current_product.subcategory.set(subcategory_ids)

        # Save custom field values
        for field in current_product.custom_fields.all():
            field_key = f"custom_{field.id}"
            value = request.POST.get(field_key)
            if value is not None:
                field.default_value = value
                field.save()

        current_product.save()

    
    content = {
        'current_template': current_template,
        'prod_id': prod_id,
        'current_product': current_product,
        'selected_subcategories_json': json.dumps(selected_subcats),
        'categories': categories,
        'templates': templates,
        'stocks': stocks,
        'avg_rating': avg_rating
    }
    return render(request, "dashboard/inventoryPages/editProduct.html", content)




def get_subcategories(request):
    category_ids = request.GET.getlist('category_ids[]')  
    subcategories = SubCategory.objects.filter(category_id__in=category_ids)

    data = [
        {"id": sub.subcat_id, "title": sub.title, "cat_id": sub.category.id}
        for sub in subcategories
    ]
    return JsonResponse({"subcategories": data})



@superadmin_required
def Products(request, page, cat_id):
    if page == "Stock":
        all = Stock.objects.all()
        chosen = Stock.objects.filter(stock_id=cat_id).first()
        products = Template.objects.filter(stock=chosen) if chosen else []
    elif page == "Category":
        all = Category.objects.all()
        chosen = Category.objects.filter(cat_id=cat_id).first()
        products = Template.objects.filter(category=chosen) if chosen else []
    elif page == "Template":
        all = Template.objects.filter(type="template")
        chosen = Template.objects.filter(tem_id=cat_id).first()
        products = Template.objects.filter(tem_id=cat_id, type="product") if chosen else []

    products = products.annotate(
    avg_rating=Coalesce(
        Avg("reviews__rating", filter=Q(reviews__is_approved=True)),
        0.0
    ),
    avg_rating_int=Coalesce(
        Round(Avg("reviews__rating", filter=Q(reviews__is_approved=True))),
        0,
        output_field=IntegerField()
    ),
    rating_count=Count(
        "reviews",
        filter=Q(reviews__is_approved=True)
    )
)     
    content = {
        'all':all,
        'chosen':chosen,
        'page':page,
        'products':products

    }
    return render(request, "dashboard/inventoryPages/products.html", content)



@superadmin_required
def DeleteProduct(request, prod_id):
    product = get_object_or_404(Template, prod_id=prod_id, type="product")

    try:
        available = int(product.available_product or 0)
        stock = int(product.stock_product or 0)

        if available != stock:
            return HttpResponseBadRequest(
                f"Cannot delete this product because it has sales data.\n"
                f"(Available: {available}, In Stock: {stock})"
            )

    except (ValueError, TypeError):
        return HttpResponseBadRequest("Invalid numeric data in product fields")
    
    if product.img:
        product.img.delete(save=False)

    # Delete if checks pass
    product.delete()

    # Redirect to previous page
    return redirect(request.META.get('HTTP_REFERER', '/'))




@superadmin_required
@require_POST
def toggle_review_status(request):
    review_id = request.POST.get("review_id")

    review = get_object_or_404(ProductReview, id=review_id)
    review.is_approved = not review.is_approved
    review.save(update_fields=["is_approved"])

    return JsonResponse({
        "success": True,
        "is_approved": review.is_approved
    })


@superadmin_required
@require_POST
def delete_review(request):
    review_id = request.POST.get("review_id")

    review = get_object_or_404(ProductReview, id=review_id)
    review.delete()

    return JsonResponse({"success": True})