from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('stakeholders/new', views.populate_stake_holders, name='populateStakeHolders'),
    path('stakeholders', views.get_stake_holders, name='getStakeHolders'),
    path('stakeholders/<str:address>/transactions/new', views.populate_transaction, name='populationTransactions')
]