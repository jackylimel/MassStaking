from django.urls import path
from . import views

urlpatterns = [
    path('stakeholders/new', views.populate_stake_holders, name='populateStakeHolders'),
    path('stakeholders', views.get_stake_holders_with_csv, name='getStakeHoldersWithCSV'),
    path('transactions/new', views.populate_transactions, name='populateTransactions'),
]
