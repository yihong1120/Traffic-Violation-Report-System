from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.conf import settings
from multiupload.fields import MultiFileField
from datetime import datetime
import pytz
from .models import TrafficViolation

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise ValidationError("這個用戶名已被使用")
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError("這個電子郵件地址已被使用")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
    
class ReportForm(forms.Form):
    VIOLATIONS = TrafficViolation.VIOLATIONS
    STATUS = TrafficViolation.STATUS

    HOUR_CHOICES = [(i, f'{i:02}') for i in range(24)]
    MINUTE_CHOICES = [(i, f'{i:02}') for i in range(60)]

    tz = pytz.timezone('Asia/Taipei')
    current_time = datetime.now(tz)

    license_plate = forms.CharField(label="車號", max_length=10)
    date = forms.DateField(label="日期", widget=forms.SelectDateWidget, initial=current_time.date(), required=False)
    hour = forms.ChoiceField(choices=HOUR_CHOICES, initial=current_time.hour, label="小時")
    minute = forms.ChoiceField(choices=MINUTE_CHOICES, initial=current_time.minute, label="分鐘")
    violation = forms.ChoiceField(label="違規項目", choices=VIOLATIONS, initial='其他')
    status = forms.ChoiceField(label="檢舉結果", choices=STATUS, initial='其他')
    location = forms.CharField(label="地點", max_length=100)
    officer = forms.CharField(label="承辦人", max_length=100, required=False)
    media = MultiFileField(label="媒體", min_num=1, max_num=5, max_file_size = settings.FILE_UPLOAD_MAX_MEMORY_SIZE)

    def clean(self):
        cleaned_data = super().clean()
        hour = cleaned_data.get("hour")
        minute = cleaned_data.get("minute")

        # 验证 hour 和 minute 的值
        if hour is None or minute is None:
            raise forms.ValidationError("You must select a valid hour and minute.")
        
        # 组合 hour 和 minute 成为一个 time 字符串
        time_string = f"{hour}:{minute}"
        cleaned_data['time'] = datetime.strptime(time_string, "%H:%M").time()
        
        return cleaned_data