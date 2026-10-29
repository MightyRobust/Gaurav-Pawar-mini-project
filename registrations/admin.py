import csv
from django.contrib import admin
from django.http import HttpResponse
from .models import Registration, ContactMessage


@admin.action(description="Export Selected Registrations to CSV")
def export_registrations_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="registrations_export.csv"'

    writer = csv.writer(response)
    # Header row
    writer.writerow([
        "ID", "Full Name", "Email", "Phone", "Team Name", 
        "Branch & Sem", "Age", "Gender", "Sport", "Registered At"
    ])

    # Data rows
    for reg in queryset:
        writer.writerow([
            reg.id,
            reg.full_name,
            reg.email,
            reg.phone,
            getattr(reg, "team_name", "") or "",
            getattr(reg, "branch_sem", "") or "",
            getattr(reg, "age", "") or "",
            reg.get_gender_display() if hasattr(reg, "get_gender_display") and reg.gender else reg.gender or "",
            reg.get_sport_display() if hasattr(reg, "get_sport_display") and reg.sport else reg.sport or "",
            reg.registered_at.strftime("%Y-%m-%d %H:%M:%S") if getattr(reg, "registered_at", None) else "",
        ])

    return response


@admin.action(description="Export Selected Contact Messages to CSV")
def export_contact_messages_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="contact_messages_export.csv"'

    writer = csv.writer(response)
    writer.writerow(["ID", "Full Name", "Email", "Phone", "Message", "Created At"])

    for msg in queryset:
        writer.writerow([
            msg.id,
            msg.fullname,
            msg.email,
            msg.phone,
            msg.message,
            msg.created_at.strftime("%Y-%m-%d %H:%M:%S") if getattr(msg, "created_at", None) else "",
        ])

    return response


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = (
        'full_name', 
        'email', 
        'phone', 
        'team_name', 
        'branch_sem', 
        'gender', 
        'sport', 
        'registered_at'
    )
    list_filter = ('sport', 'gender', 'branch_sem', 'registered_at')
    search_fields = ('full_name', 'email', 'phone', 'team_name')
    ordering = ('-registered_at',)
    actions = [export_registrations_csv]


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('fullname', 'email', 'phone', 'short_message', 'created_at')
    search_fields = ('fullname', 'email', 'phone', 'message')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    readonly_fields = ('fullname', 'phone', 'email', 'message', 'created_at')
    actions = [export_contact_messages_csv]

    def short_message(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    short_message.short_description = 'Message'