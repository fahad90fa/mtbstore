from xmlrpc import client
from django.shortcuts import render, get_object_or_404, redirect
from accounts.decorator import superadmin_required
from accounts.models import CustomUser
from dashboard.models import DraftInvoice, DraftInvoiceItem, Template
from django.db.models import Count
from decimal import Decimal
from django.db import transaction
from merchants.models import Invoice, InvoiceItem


@superadmin_required
def AdminProfile(request):
    Employees_count = CustomUser.objects.filter(account_type="Employee").count()
    Merchants_count = CustomUser.objects.filter(account_type="Merchant").count()
    Clients_count = CustomUser.objects.filter(account_type="Client").count()
    context = {'Employees_count': Employees_count, 'Merchants_count': Merchants_count, 'Clients_count': Clients_count}
    return render(request, 'dashboard/profile/profile.html', context)


@superadmin_required
def AdminSettings(request):
    Employees_count = CustomUser.objects.filter(account_type="Employee").count()
    Merchants_count = CustomUser.objects.filter(account_type="Merchant").count()
    Clients_count = CustomUser.objects.filter(account_type="Client").count()
    if request.method == 'POST':
        superadmin = request.user
        superadmin.first_name = request.POST.get("fname")
        superadmin.last_name = request.POST.get("lname")
        superadmin.address = request.POST.get("address")
        superadmin.email = request.POST.get("email")
        superadmin.mobile_number = request.POST.get("phone")
        superadmin.cnic = request.POST.get("cnic")
        profile_pic = request.FILES.get('avatar')
        if profile_pic:
            superadmin.profile_pic = profile_pic
        superadmin.save()
        return redirect(request.META.get('HTTP_REFERER', '/'))
    context = {'Employees_count': Employees_count, 'Merchants_count': Merchants_count, 'Clients_count': Clients_count}
    return render(request, 'dashboard/profile/settings.html', context)




def apply_invoice_side_effects(invoice):
    with transaction.atomic():
        for item in invoice.items.select_for_update():
            qty = int(item.quantity or 0)

            # PRODUCT row
            product = Template.objects.select_for_update().filter(
                type="product",
                prod_id=item.product_code
            ).first()

            if not product:
                continue

            # update product counters
            product.available_product = str(
                max(0, int(product.available_product or 0) - qty)
            )
            product.sold_product = str(
                int(product.sold_product or 0) + qty
            )
            product.save(update_fields=["available_product", "sold_product"])

            # update stock
            if product.stock:
                stock = product.stock
                stock.sold_product = str(
                    int(stock.sold_product or 0) + qty
                )
                stock.save(update_fields=["sold_product"])

            # PARENT TEMPLATE row (linked by tem_id)
            parent_template = Template.objects.select_for_update().filter(
                type="template",
                tem_id=product.tem_id
            ).first()

            if parent_template:
                parent_template.sold_product = str(
                    int(parent_template.sold_product or 0) + qty
                )
                parent_template.save(update_fields=["sold_product"])

        # client balance
        client = CustomUser.objects.select_for_update().filter(
            mtb_id=invoice.merchant_id
        ).first()

        if client:
            client.client_balance = str(
                Decimal(client.client_balance or "0") +
                Decimal(invoice.total)
            )
            client.save(update_fields=["client_balance"])
@superadmin_required
def AdminInvoice(request):
    Employees_count = CustomUser.objects.filter(account_type="Employee").count()
    Merchants_count = CustomUser.objects.filter(account_type="Merchant").count()
    Clients_count = CustomUser.objects.filter(account_type="Client").count()
    clients = CustomUser.objects.filter(account_type="Client")

    products = [
        p for p in Template.objects.filter(type="product")
        if int(p.available_product or 0) > 0
    ]

    active_draft = None
    message = None

    # ✅ LOAD ACTIVE DRAFT FROM GET (for resume after redirect)
    draft_param = request.GET.get("draft")
    if draft_param:
        active_draft = DraftInvoice.objects.filter(
            draft_id=draft_param,
            user=request.user,
            status="draft"
        ).first()

    if request.method == "POST":
        action = request.POST.get("action")
        draft_id = request.POST.get("draft_id")

        # =========================
        # RESUME DRAFT
        # =========================
        if action == "resume":
            return redirect(f"{request.path}?draft={draft_id}")

        # =========================
        # DISCARD DRAFT
        # =========================
        elif action == "discard":
            draft = get_object_or_404(
                DraftInvoice,
                draft_id=draft_id,
                user=request.user
            )
            draft.status = "abandoned"
            draft.save()
            return redirect(request.path)

        # =========================
        # FINALIZE EXISTING DRAFT
        # =========================
        elif action == "finalize_existing":
            draft = get_object_or_404(
                DraftInvoice,
                draft_id=draft_id,
                user=request.user
            )
            client = CustomUser.objects.filter(mtb_id=draft.client_id).first()
            prev_balance = Decimal(client.client_balance or "0") if client else Decimal("0")
            invoice = Invoice.objects.create(
                merchant_id=draft.client_id,
                total=draft.subtotal,
                debit=draft.subtotal,
                credit="0",
                balance=prev_balance + Decimal(draft.subtotal),
                payment_method=draft.payment_method,
                payment_reference=draft.payment_reference,
                date=draft.date,
                source_type="ClientInvoice"
            )

            for item in draft.items.all():
                InvoiceItem.objects.create(
                    invoice=invoice,
                    product_name=item.product_name,
                    rate=item.price,
                    quantity=item.quantity,
                    amount=item.total,
                    product_code=item.product_id
                )
            apply_invoice_side_effects(invoice)
            draft.status = "finalized"
            draft.save()
            return redirect(request.path)

        # =========================
        # CREATE / UPDATE DRAFT OR FINAL
        # =========================
        elif action in ("draft", "final"):
            client_id = request.POST.get("client_id")
            payment_method = request.POST.get("payment_method", "")
            payment_reference = request.POST.get("payment_reference", "")
            invoice_date = request.POST.get("invoice_date", "")

            # ✅ ALWAYS define first
            existing_items = {}

            if draft_id:
                active_draft = get_object_or_404(
                    DraftInvoice,
                    draft_id=draft_id,
                    user=request.user,
                    status="draft"
                )

                # map existing items (popup + previous saves)
                existing_items = {
                    item.product_id: item
                    for item in active_draft.items.all()
                }

                active_draft.client_id = client_id
                active_draft.payment_method = payment_method
                active_draft.payment_reference = payment_reference
                active_draft.date = invoice_date
                active_draft.save()
            else:
                active_draft = DraftInvoice.objects.create(
                    user=request.user,
                    client_id=client_id,
                    payment_method=payment_method,
                    payment_reference=payment_reference,
                    date=invoice_date,
                    subtotal="0",
                    status="draft"
                )

            selected_products = request.POST.getlist("products[]")

            for p in Template.objects.filter(prod_id__in=selected_products):
                posted_price = request.POST.get(f"price_{p.prod_id}", "").strip()
                final_price = posted_price if posted_price else (p.base_price or "0")
                price = Decimal(str(final_price))

                qty = int(request.POST.get(f"qty_{p.prod_id}", 1))
                line_total = price * qty

                if p.prod_id in existing_items:
                    item = existing_items[p.prod_id]
                    item.price = price
                    item.quantity = qty
                    item.total = line_total
                    item.save()
                else:
                    DraftInvoiceItem.objects.create(
                        draft=active_draft,
                        product_id=p.prod_id,
                        product_name=p.title,
                        price=price,
                        quantity=qty,
                        total=line_total
                    )

            # ✅ single source of truth for subtotal
            active_draft.subtotal = sum(
                item.price * item.quantity
                for item in active_draft.items.all()
            )
            active_draft.save()

            if action == "final":
                client = CustomUser.objects.filter(mtb_id=active_draft.client_id).first()
                prev_balance = Decimal(client.client_balance or "0") if client else Decimal("0")
                invoice = Invoice.objects.create(
                    merchant_id=active_draft.client_id,
                    total=active_draft.subtotal,
                    debit=active_draft.subtotal,
                    credit="0",
                    balance=prev_balance + Decimal(active_draft.subtotal),
                    payment_method=active_draft.payment_method,
                    payment_reference=active_draft.payment_reference,
                    date=active_draft.date,
                    source_type="ClientInvoice"
                )

                for item in active_draft.items.all():
                    InvoiceItem.objects.create(
                        invoice=invoice,
                        product_name=item.product_name,
                        rate=item.price,
                        quantity=item.quantity,
                        amount=item.total,
                        product_code=item.product_id
                    )
                apply_invoice_side_effects(invoice)

                active_draft.status = "finalized"
                active_draft.save()
                return redirect(request.path)

            return redirect(f"{request.path}?draft={active_draft.draft_id}")


    # 🔄 ALWAYS reload drafts AFTER any POST
    draft_invoices = (
        DraftInvoice.objects
        .filter(user=request.user, status="draft")
        .annotate(items_count=Count("items"))
        .order_by("-created_at")
    )

    client_map = {
        c.mtb_id: f"{c.first_name} {c.last_name}"
        for c in clients
    }

    for inv in draft_invoices:
        inv.client_name = client_map.get(inv.client_id, "—")

    context = {
        "products": products,
        "clients": clients,
        "draft_invoices": draft_invoices,
        "active_draft": active_draft,
        "message": message,
        'Employees_count': Employees_count,
        'Merchants_count': Merchants_count,
        'Clients_count': Clients_count
    }

    return render(request, "dashboard/profile/invoice.html", context)



@superadmin_required
def popup_add_product_to_invoice(request):
    if request.method != "POST":
        return redirect(request.META.get("HTTP_REFERER", "/"))

    product_id = request.POST.get("product_id")
    draft_id = request.POST.get("draft_id")
    quantity = int(request.POST.get("quantity", 1))

    product = get_object_or_404(Template, prod_id=product_id)

    # create or get draft
    if draft_id == "new":
        draft = DraftInvoice.objects.create(user=request.user)
    else:
        draft = get_object_or_404(
            DraftInvoice,
            draft_id=draft_id,
            user=request.user,
            status="draft"
        )

    raw_price = (product.base_price or "0").strip()
    price = Decimal(raw_price) if raw_price.replace(".", "", 1).isdigit() else Decimal("0")

    total = price * quantity

    DraftInvoiceItem.objects.create(
        draft=draft,
        product_id=product.prod_id,
        product_name=product.title,
        price=price,
        quantity=quantity,
        total=total
    )

    draft.subtotal = sum(
    (item.price * item.quantity) for item in draft.items.all()
)
    draft.save()


    return redirect(request.META.get("HTTP_REFERER", "/"))



@superadmin_required
def InvoicePreview(request):
    if request.method != "POST":
        return redirect("AdminInvoice")

    draft_id = request.POST.get("draft_id")

    draft = get_object_or_404(
        DraftInvoice,
        draft_id=draft_id,
        user=request.user,
        status="draft"   # only allow preview of active draft
    )

    merchant = CustomUser.objects.filter(
        mtb_id=draft.client_id
    ).first()

    items = draft.items.all()

    # Dummy invoice object (NOT saved)
    class DummyInvoice:
        def __init__(self, draft):
            self.invoice_id = f"DRAFT-{draft.draft_id}"
            self.date = draft.date
            self.total = draft.subtotal
            self.debit = draft.subtotal
            self.credit = Decimal("0")
            self.balance = draft.subtotal
            self.payment_method = draft.payment_method
            self.payment_reference = draft.payment_reference
            self.source_type = "Payment"  # or dynamic if needed

    invoice = DummyInvoice(draft)

    context = {
        "invoice": invoice,
        "merchant": merchant,
        "items": items,
    }

    return render(
        request,
        "invoices/stock_invoice.html",
        context
    )