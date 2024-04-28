# Generated by Django 4.2.6 on 2024-04-28 13:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food_recommendation', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RecommendedFood',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('food_name', models.CharField(max_length=100)),
                ('recommended_on', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]