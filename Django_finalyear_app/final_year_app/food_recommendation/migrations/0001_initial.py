# Generated by Django 4.2.6 on 2024-04-28 13:27

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RecommendedDrink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('drink_name', models.CharField(max_length=100)),
                ('recommended_on', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
