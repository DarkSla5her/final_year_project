# Generated by Django 4.2.6 on 2024-04-28 15:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import food_recommendation.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('food_recommendation', '0002_recommendedfood'),
    ]

    operations = [
        migrations.AddField(
            model_name='recommendeddrink',
            name='user',
            field=models.ForeignKey(default=food_recommendation.models.get_default_user, on_delete=django.db.models.deletion.CASCADE, related_name='recommended_drinks', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='recommendedfood',
            name='user',
            field=models.ForeignKey(default=food_recommendation.models.get_default_user, on_delete=django.db.models.deletion.CASCADE, related_name='recommended_foods', to=settings.AUTH_USER_MODEL),
        ),
    ]