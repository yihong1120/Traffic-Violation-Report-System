# Generated by Django 4.2.7 on 2023-11-19 06:50

from django.db import migrations, models
import reports.models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='trafficviolation',
            name='username',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='mediafile',
            name='file',
            field=models.FileField(upload_to=reports.models.PathAndRename('')),
        ),
        migrations.AlterField(
            model_name='trafficviolation',
            name='violation',
            field=models.CharField(choices=[('紅線停車', '紅線停車'), ('黃線臨車', '黃線臨車'), ('行駛人行道', '行駛人行道'), ('未停讓行人', '未停讓行人'), ('切換車道未打方向燈', '切換車道未打方向燈'), ('人行道停車', '人行道停車'), ('騎樓停車', '騎樓停車'), ('闖紅燈', '闖紅燈'), ('逼車', '逼車'), ('未禮讓直行車', '未禮讓直行車'), ('未依標線行駛', '未依標線行駛'), ('其他', '其他')], max_length=100),
        ),
    ]