from django.urls import path
from .views.stakeholders import *
from .views.transactions import *

urlpatterns = [
    path('stakeholders/new', populate_stake_holders, name='populateStakeHolders'),
    path('stakeholders', get_stake_holders_with_csv, name='getStakeHoldersWithCSV'),
    path('transactions/new', populate_transactions, name='populateTransactions'),
]
