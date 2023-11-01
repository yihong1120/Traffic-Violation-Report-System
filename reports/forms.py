from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from multiupload.fields import MultiFileField
from datetime import datetime
import pytz
from .models import TrafficViolation

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
    
class ReportForm(forms.Form):
    VIOLATIONS = TrafficViolation.VIOLATIONS
    STATUS = TrafficViolation.STATUS

    # 建立選項
    HOUR_CHOICES = [(i, f'{i:02}') for i in range(24)]
    MINUTE_CHOICES = [(i, f'{i:02}') for i in range(60)]

    # 取得當前台北時間
    tz = pytz.timezone('Asia/Taipei')
    current_time = datetime.now(tz)


    license_plate = forms.CharField(label="車號", max_length=10)
    date = forms.DateField(label="日期", widget=forms.SelectDateWidget, required=False)
    hour = forms.ChoiceField(choices=HOUR_CHOICES, initial=current_time.hour, label="小時")
    minute = forms.ChoiceField(choices=MINUTE_CHOICES, initial=current_time.minute, label="分鐘")
    violation = forms.ChoiceField(label="違規項目", choices=VIOLATIONS, initial='其他')
    status = forms.ChoiceField(label="檢舉結果", choices=STATUS, initial='其他')
    location = forms.CharField(label="地點", max_length=100)
    officer = forms.CharField(label="承辦人", max_length=100, required=False)
    # media = forms.FileField(label="媒體", widget=forms.ClearableFileInput(attrs={'multiple': True}))
    media = MultiFileField(label="媒體", min_num=1, max_num=10, max_file_size=1024*1024*500)  # 最多允許上傳10個文件，每個文件最大500MB