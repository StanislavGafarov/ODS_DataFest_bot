# Generated by Django 2.1.7 on 2019-04-19 19:54
from django.db import migrations, models
class Migration(migrations.Migration):
    dependencies = [
        ('backend', '0012_auto_20190419_0617'),
    ]
    operations = [
        migrations.AddField(
            model_name='randombeeruser',
            name='email',
            field=models.TextField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name='randombeeruser',
            name='random_beer_try',
            field=models.IntegerField(default=0),
        ),
    ]