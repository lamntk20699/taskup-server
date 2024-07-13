from django.contrib import admin

# Register your models here.
from taskup_api.models import MemberInfo
from .models import UserAccount

from .forms import CustomUserCreationForm

# @admin.register(MemberInfo)
# class PersonAdmin(admin.ModelAdmin):
#     list_display = ("memberId", "fullName", "account")
#     pass

@admin.register(UserAccount)
class UserAdmin(admin.ModelAdmin):
    form = CustomUserCreationForm
    list_display = ('email', 'account', 'last_name', 'first_name',)
    # fieldsets = (
    #     (None, {
    #         'fields': ('first_name', 'last_name', 'email', 'password')
    #     }),
    # )

    def delete_model(self, request, obj):
        memberQueryset = MemberInfo.objects.filter(email=str(obj))
        if memberQueryset.exists():
            member = memberQueryset[0]
            member.delete()
        return super().delete_model(request, obj)
