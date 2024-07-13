import random
from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from taskup_api.models import MemberInfo
from taskup_api.serializers import MemberSerializer
# Import custom user model
from django.contrib.auth import get_user_model
custom_user_model = get_user_model()

def generate_random_user_id():
    return str(random.randint(10**8, 10**9 - 1))

class CustomUserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""

    # username = forms.CharField(label='Username', min_length=4, max_length=150)
    email = forms.EmailField(label='Email')
    first_name = forms.CharField(label='First Name')
    last_name = forms.CharField(label='Last Name')
    account = forms.CharField(label='Account', max_length=20)

    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = custom_user_model
        fields = ('first_name', 'last_name', 'account')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        email = self.cleaned_data["email"]
        account = self.cleaned_data["account"]
        first_name = self.cleaned_data["first_name"]
        last_name = self.cleaned_data["last_name"]
        fullName = last_name + " " + first_name
        memberQueryset = MemberInfo.objects.filter(email=email)
        if memberQueryset.exists():
            member = memberQueryset[0]
            setattr(member, "fullName", fullName)
            setattr(member, "account", account)
            setattr(member, "email", email)
            member.save()
        else:
            flag = True
            memberId = ""
            while flag:
                memberId = generate_random_user_id()
                existedMember = MemberInfo.objects.filter(memberId=memberId)
                if not existedMember.exists():
                    flag = False;

            newMember = MemberInfo(
                memberId = memberId,
                fullName = fullName,
                account = account,
                email = email
            )
            newMember.save()

        if commit:
            user.save()

        return user
