from django.urls import path

from .views.stakeholders import *

urlpatterns = [
    path('stakeholders/new', populate_stake_holders, name='populateStakeHolders'),
    path('transactions/new', populate_transactions, name='populateTransactions'),
]
