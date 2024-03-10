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
    ...


@admin.register(Scheduler)
class SchedulerAdmin(admin.ModelAdmin):
    list_display = ('frequency', 'time_of_day')
