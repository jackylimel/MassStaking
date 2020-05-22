from functools import reduce

import requests
from django.http import HttpResponse
from django.template import loader

from .models import *
from .view_models import *


# Create your views here.
def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def populate_stake_holders(request):
    r = requests.get('https://explorerapi.masscafe.cn/v1/explorer/transactions/staking/reward/top/?limit=30')
    data_set = r.json()['data']
    now = datetime.now()
    timestamp = datetime.timestamp(now)
    stake_holders = map(lambda data: _data_to_stake_holder(data, timestamp), data_set)
    for holder in stake_holders:
        print(holder)
        holder.save()
    return HttpResponse("success")


def get_stake_holders(request):
    stake_holders = StakeHolder.objects.filter(receiving_reward=True)
    holder_view_models = map(lambda holder: __map_stake_holder_to_view_model(holder), stake_holders)
    total = reduce(lambda accu, result: accu + float(result.total_amount), stake_holders, 0)
    template = loader.get_template('staking/index.html')
    context = {
        'stake_holders': holder_view_models,
        'total_amount': total
    }
    return HttpResponse(template.render(context, request))


def __map_stake_holder_to_view_model(stakeholder):
    holder_view_model = StakingViewModel(stakeholder)
    transactions = Transaction.objects.filter(holder_address=stakeholder.address)
    holder_view_model.add_transactions(
        map(lambda tx: TransactionViewModel(tx), transactions)
    )
    return holder_view_model


def populate_transaction(request, address):
    url = ('https://explorerapi.masscafe.cn/v1/explorer/addresses/%s/?page=1&tx_type=1' % address)
    transactions = _get_transactions_from(address, url)
    for transaction in transactions:
        transaction.save()
    return HttpResponse()


def _get_transactions_from(address, url):
    print('fetching data from url: %s' % url)
    json = requests.get(url).json()
    transaction_list = requests.get(url).json()['results']['data']['transaction_list']
    transactions = list(map(lambda data: _data_to_transaction(address, data), transaction_list))

    if json['next'] is not None:
        transactions.extend(_get_transactions_from(address, json['next']))
    return transactions


def _data_to_transaction(address, data):
    transaction = Transaction(hash=data['txhash'], amount=data['collect'],
                              timestamp=data['tx']['block']['timestamp'], holder_address=address)
    return transaction


def _data_to_stake_holder(data, timestamp):
    return StakeHolder(address=data['address'], total_amount=data['total_amount'],
                       order=data['id'], timestamp=timestamp, receiving_reward=True)
