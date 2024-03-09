from django.contrib import admin

from .models import *


@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    ...


@admin.register(SendList)
class SendListAdmin(admin.ModelAdmin):
    ...


@admin.register(Footer)
class FooterAdmin(admin.ModelAdmin):
    ...


@admin.register(Dispatch)
class DispatchAdmin(admin.ModelAdmin):
    ...
