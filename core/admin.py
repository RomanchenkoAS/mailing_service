from django import forms
from django.contrib import admin

from .models import *


@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    ...


@admin.register(SendList)
class SendListAdmin(admin.ModelAdmin):
    ...


class FooterAdminForm(forms.ModelForm):
    class Meta:
        model = Footer
        fields = '__all__'
        widgets = {
            'text': forms.Textarea(attrs={'rows': 10, 'cols': 40}),
        }


@admin.register(Footer)
class FooterAdmin(admin.ModelAdmin):
    form = FooterAdminForm


@admin.register(Dispatch)
class DispatchAdmin(admin.ModelAdmin):
    list_display = ('title', 'last_sent_at', 'next_due_at', 'get_recipient_count_display')
    actions = ['send_now', 'toggle_activation']

    def get_recipient_count_display(self, obj):
        return obj.get_recipient_count()

    get_recipient_count_display.short_description = 'Recipient Count'

    def send_now(self, request, queryset):
        for dispatch in queryset:
            dispatch.send()

    send_now.short_description = "Send selected dispatches now"

    def toggle_activation(self, request, queryset):
        for dispatch in queryset:
            dispatch.toggle_activation()

    toggle_activation.short_description = "Toggle activation of selected dispatches"


@admin.register(Scheduler)
class SchedulerAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["frequency", "time_of_day"]
        return super().get_readonly_fields(request, obj)
