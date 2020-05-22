from django.db import models


# Create your models here.
class StakeHolder(models.Model):
    address = models.CharField(max_length=100)
    total_amount = models.FloatField()
    order = models.IntegerField()
    timestamp = models.CharField(max_length=50)
    receiving_reward = models.BooleanField()

    def __str__(self):
        return ','.join(map(lambda key: '{key} = {value}'.format(key=key, value=self.__dict__.get(key)), self.__dict__))


class Transaction(models.Model):
    hash = models.CharField(max_length=100, primary_key=True)
    holder_address = models.CharField(max_length=100)
    timestamp = models.CharField(max_length=100)
    amount = models.FloatField()

    def __str__(self):
        return ','.join(map(lambda key: '{key} = {value}'.format(key=key, value=self.__dict__.get(key)), self.__dict__))
