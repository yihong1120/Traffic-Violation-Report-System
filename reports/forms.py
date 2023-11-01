from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from multiupload.fields import MultiFileField
from datetime import datetime
import pytz

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
    VIOLATIONS = [
        ('紅線停車', '紅線停車'),
        ('行駛人行道', '行駛人行道'),
        ('未停讓行人', '未停讓行人'),
        ('切換車道未打方向燈', '切換車道未打方向燈'),
        ('人行道騎樓停車', '人行道騎樓停車'),
        ('闖紅燈', '闖紅燈'),
        ('逼車', '逼車'),
        ('未禮讓直行車', '未禮讓直行車'),
        ('未依標線行駛', '未依標線行駛'),
        ('其他', '其他')
    ]
    STATUS = [
        ('通過', '通過'),
        ('未通過', '未通過'),
        ('其他', '其他')
    ]
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