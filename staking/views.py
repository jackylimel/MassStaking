import time
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
        holder.save()
    return HttpResponse("success")


def get_stake_holders(request):
    stake_holders = _load_stake_holders()
    transaction_view_models = list(map(lambda tx: TransactionViewModel(tx), _load_transactions()))

    holder_view_models = map(lambda holder: _map_stake_holder_to_view_model(holder, transaction_view_models),
                             stake_holders)
    sorted_transaction_view_models = sorted(transaction_view_models, key=lambda tx: tx.timestamp)
    total = reduce(lambda accu, result: accu + float(result.total_amount), stake_holders, 0)

    template = loader.get_template('staking/index.html')
    context = {
        'stake_holders': holder_view_models,
        'sorted_transactions': sorted_transaction_view_models,
        'total_amount': total
    }
    return HttpResponse(template.render(context, request))


def _map_stake_holder_to_view_model(stakeholder, transaction_view_models):
    holder_view_model = StakingViewModel(stakeholder)
    filtered_transactions = list(filter(lambda tx: tx.holder_address == stakeholder.address, transaction_view_models))
    holder_view_model.add_transactions(filtered_transactions)
    return holder_view_model


def _load_stake_holders():
    return StakeHolder.objects.filter(receiving_reward=True)


def _load_transactions():
    locking_timestamp = datetime.timestamp(datetime.now()) - 61440 * 45
    return Transaction.objects.filter(amount__gt=0, timestamp__gte=locking_timestamp)


def populate_transactions(request):
    stake_holders = StakeHolder.objects.filter(receiving_reward=True)
    for holder in stake_holders:
        address = holder.address
        print('populate transactions for address: %s' % address)
        url = ('https://explorerapi.masscafe.cn/v1/explorer/addresses/%s/?page=1&tx_type=1' % address)
        transactions = _get_transactions_from(address, url)
        for transaction in transactions:
            transaction.save()
    return HttpResponse()


def _get_transactions_from(address, url):
    print('fetching data from url: %s' % url)
    time.sleep(1)
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
