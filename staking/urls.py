from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('stakeholders/new', views.populate_stake_holders, name='populateStakeHolders'),
    path('csv/stakeholders', views.get_stake_holders_with_csv, name='getStakeHoldersWithCSV'),
    path('csv/transactions', views.get_transactions_with_csv, name='getTransactionsWithCSV'),
    path('csv/summary', views.get_transaction_sum_with_csv, name='getTransactionSummaryWithCSV'),
    path('transactions/new', views.populate_transactions, name='populationAllTransactions')
]
