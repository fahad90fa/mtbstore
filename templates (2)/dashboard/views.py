from django.forms import IntegerField
from django.shortcuts import render, HttpResponse, get_object_or_404, redirect
from accounts.decorator import superadmin_required
from django.views.decorators.http import require_POST
from django.utils.timezone import now
from .models import Alert, DraftInvoice, Template
from django.http import JsonResponse
from ecom.models import ContactMessage
from django.db.models import Count
from django.db.models.functions import Cast
from django.utils import timezone
from datetime import timedelta
# Create your views here.


@superadmin_required
def alerts_api(request):
    current_time = now()

    alerts = Alert.objects.filter(
        status='awaiting',
        datetime__lte=current_time
    ).filter(
        expiration_datetime__isnull=True
    ) | Alert.objects.filter(
        status='awaiting',
        datetime__lte=current_time,
        expiration_datetime__gt=current_time
    )

    data = [
        {
            "id": alert.id,
            "text": alert.text,
            "status": alert.status,
            "datetime": alert.datetime.strftime("%Y-%m-%d %H:%M"),
        }
        for alert in alerts
    ]

    return JsonResponse({"alerts": data})

@require_POST
@superadmin_required
def mark_alert_read(request, alert_id):
    try:
        alert = Alert.objects.get(id=alert_id)
        alert.status = 'read'
        alert.save()
        return JsonResponse({"success": True})
    except Alert.DoesNotExist:
        return JsonResponse({"success": False}, status=404)
    

@superadmin_required
def templates_api(request):
    template_type = "template"

    qs = Template.objects.filter(type=template_type)
    
    data = list(
        qs.values("tem_id", "template_name")
    )
    return JsonResponse(data, safe=False)

@superadmin_required
def popup_fetch_drafts(request):
    drafts = (
        DraftInvoice.objects
        .filter(user=request.user, status="draft")
        .annotate(items_count=Count("items"))
        .order_by("-created_at")
    )

    data = [
        {
            "draft_id": d.draft_id,
            "items_count": d.items_count
        }
        for d in drafts
    ]

    return JsonResponse(data, safe=False)

# ───────────────────────────────

    # Help & Reports

# ───────────────────────────────


@superadmin_required
def HelpReports(request):
    contact_messages = (
        ContactMessage.objects
        .order_by("is_read", "-created_at")
    )
    content = {
        'contact_messages': contact_messages,}
    return render(request, "dashboard/helpReports.html", content)
@superadmin_required
def HelpReportsRead(request, pk):
    msg = get_object_or_404(ContactMessage, pk=pk)
    msg.is_read = True
    msg.save()
    return redirect("HelpReports")

@superadmin_required
def HelpReportsDelete(request, pk):
    msg = get_object_or_404(ContactMessage, pk=pk)
    msg.delete()
    return redirect("HelpReports")