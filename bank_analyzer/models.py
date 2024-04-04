from django.db import models

class Transaction(models.Model):
    card_id = models.IntegerField(verbose_name = 'id карты')
    amount = models.IntegerField(verbose_name = 'сумма')
    shop = models.CharField(max_length = 100, verbose_name = 'название магазина')
    dt = models.DateTimeField(blank = True, null = True, verbose_name = 'дата и время платежа')