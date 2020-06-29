from enum import Enum

from django.db import models


# Create your models here.
class Holder(models.Model):
    address = models.CharField(max_length=100)
    total_amount = models.FloatField()
    order = models.IntegerField()
    timestamp = models.CharField(max_length=50)
    receiving_reward = models.BooleanField()
    type = models.CharField(max_length=20)

    def __str__(self):
        return 'Address: {0}, Rank: {1}, Amount: {2}, Timestamp: {3}'.format(self.address, self.order,
                                                                             self.total_amount, self.timestamp)


class Transaction(models.Model):
    hash = models.CharField(max_length=100, primary_key=True)
    holder_address = models.CharField(max_length=100)
    timestamp = models.CharField(max_length=100)
    amount = models.FloatField()
    block = models.IntegerField()

    def __str__(self):
        return ','.join(map(lambda key: '{key} = {value}'.format(key=key, value=self.__dict__.get(key)), self.__dict__))


class Binding(models.Model):
    amount = models.FloatField()
    timestamp = models.CharField(max_length=100)

    def __str__(self):
        return "Amount: {0}, Timestamp: {1}".format(self.amount, self.timestamp)


class Staking(models.Model):
    amount = models.FloatField()
    timestamp = models.CharField(max_length=100)

    def __str__(self):
        return "Amount: {0}, Timestamp: {1}".format(self.amount, self.timestamp)


class Block(models.Model):
    height = models.IntegerField()
    timestamp = models.CharField(max_length=100)

    def __str__(self):
        return "Height: {0}, Timestamp: {1}".format(self.height, self.timestamp)


class StakeHolderType(Enum):
    STAKING = "staking"
    BINDING = "binding"
    EXCHANGE = "exchange"
