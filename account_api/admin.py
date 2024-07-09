from django.contrib import admin

# Register your models here.
from taskup_api.models import MemberInfo

@admin.register(MemberInfo)
class PersonAdmin(admin.ModelAdmin):
    list_display = ("memberId", "fullName", "account")
    pass
