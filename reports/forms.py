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
    
class ReportForm(forms.ModelForm):
    class Meta:
        model = TrafficViolation
        fields = ('license_plate', 'date', 'violation', 'status', 'location', 'officer', 'media')
        # 假设这些是您模型中的字段

    # 假设模型中有 hour 和 minute 字段，我们将它们转换为 time 字段
    hour = forms.ChoiceField(choices=[(i, f"{i:02}") for i in range(24)], label="小時")
    minute = forms.ChoiceField(choices=[(i, f"{i:02}") for i in range(60)], label="分鐘")

    def clean(self):
        cleaned_data = super().clean()
        hour = cleaned_data.get("hour")
        minute = cleaned_data.get("minute")
        # 将 hour 和 minute 转换为 time 类型并设置
        cleaned_data['time'] = datetime.strptime(f"{hour}:{minute}", "%H:%M").time()
        return cleaned_data

    def save(self, commit=True):
        # 因为已经在 clean 方法中处理了 time，所以直接调用父类的 save 方法
        return super().save(commit=commit)
    
    # 如果您的模型中有一些字段不希望通过表单直接修改，可以在这里覆盖
    # 取得当前台北时间
    tz = pytz.timezone('Asia/Taipei')
    current_time = datetime.now(tz)

    # 对于日期和时间，如果模型中已经有了，就不需要在这里再定义了
    # 但如果您想要在表单中以不同的方式展现，可以像下面这样覆盖模型字段
    date = forms.DateField(
        label="日期",
        widget=forms.SelectDateWidget,
        required=False,
        initial=current_time.date()  # 使用当前日期作为默认值
    )
    hour = forms.ChoiceField(
        choices=[(i, f'{i:02}') for i in range(24)],
        initial=current_time.hour,  # 使用当前小时作为默认值
        label="小時"
    )
    minute = forms.ChoiceField(
        choices=[(i, f'{i:02}') for i in range(60)],
        initial=current_time.minute,  # 使用当前分钟作为默认值
        label="分鐘"
    )

    # 对于多文件上传，确保您的模型能够处理多个上传的文件
    # 如果模型中定义了相应的字段，MultiFileField 可以直接使用
    media = MultiFileField(
        label="媒體",
        min_num=1,
        max_num=10,
        max_file_size=1024*1024*500  # 最多允许上传10个文件，每个文件最大500MB
    )