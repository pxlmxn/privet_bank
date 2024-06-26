# Generated by Django 5.0.2 on 2024-04-04 10:58

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('card_id', models.IntegerField(verbose_name='id карты')),
                ('amount', models.IntegerField(verbose_name='сумма')),
                ('shop', models.CharField(max_length=100, verbose_name='название магазина')),
                ('dt', models.DateTimeField(verbose_name='дата и время платежа')),
            ],
        ),
    ]
