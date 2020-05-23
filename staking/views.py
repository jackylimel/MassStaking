from functools import reduce

import pandas
import requests
from django.http import HttpResponse
from django.shortcuts import render

from .models import *
from .view_models import *
from .constants import Constants


# Create your views here.
def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def populate_stake_holders(request):
    r = requests.get('https://explorerapi.masscafe.cn/v1/explorer/transactions/staking/reward/top/?limit=30')
    data_set = r.json()['data']
    timestamp = datetime.timestamp(datetime.now())
    new_stake_holders = [_data_to_stake_holder(data, timestamp) for data in data_set]
    new_stake_holder_addresses = [holder.address for holder in new_stake_holders]
    existing_stake_holders = list(_load_stake_holders())
    if len(new_stake_holder_addresses) != 0:
        filtered = [holder for holder in existing_stake_holders if holder.address not in new_stake_holder_addresses]
        for filtered_holder in filtered:
            filtered_holder.receiving_reward = False
            filtered_holder.save()
    for new_holder in new_stake_holders:
        print(new_holder)
        new_holder.save()
    return HttpResponse("success")


def _data_to_stake_holder(data, timestamp):
    return StakeHolder(address=data['address'], total_amount=data['total_amount'],
                       order=data['id'], timestamp=timestamp, receiving_reward=True)


def get_stake_holders(request):
    stake_holders = _load_stake_holders()
    transaction_view_models = list(map(lambda tx: TransactionViewModel(tx), _load_transactions()))

    holder_view_models = list(map(lambda holder: _map_stake_holder_to_view_model(holder, transaction_view_models),
                                  stake_holders))

    sorted_transaction_view_models = sorted(transaction_view_models, key=lambda tx: tx.timestamp)

    data_frame = pandas.DataFrame.from_records([vars(vm) for vm in sorted_transaction_view_models])
    tx_sum = data_frame.groupby('unlocking_day')['total'].sum()
    dic = tx_sum.to_dict()
    tx_sum_list = list(map(lambda tx: {'date': tx.to_pydatetime().date, 'value': dic[tx]}, dic))

    total = reduce(lambda accu, result: accu + float(result.total_amount), stake_holders, 0)

    context = {
        'stake_holders': holder_view_models,
        'sorted_transactions': sorted_transaction_view_models,
        'total_amount': total,
        'sum': tx_sum_list
    }
    return render(request, 'staking/index.html', context)


def _map_stake_holder_to_view_model(stakeholder, transaction_view_models):
    holder_view_model = StakingViewModel(stakeholder)
    filtered_transactions = list(filter(lambda tx: tx.holder_address == stakeholder.address, transaction_view_models))
    holder_view_model.add_transactions(filtered_transactions)
    return holder_view_model


def _load_stake_holders():
    return filter(lambda holder: holder.address not in Constants.official_addresses,
                  StakeHolder.objects.filter(receiving_reward=True))


def _load_transactions():
    locking_timestamp = datetime.timestamp(datetime.now()) - 61440 * 45
    all_transactions = Transaction.objects.filter(amount__gt=0, timestamp__gte=locking_timestamp)
    return filter(lambda tx: tx.holder_address not in Constants.official_addresses, all_transactions)


def populate_transactions(request):
    stake_holders = _load_stake_holders()
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
