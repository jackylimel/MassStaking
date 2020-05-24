from functools import reduce

import pandas
import requests
from django.http import HttpResponse
from django.shortcuts import render

import csv
from .models import *
from .view_models import *
from .constants import Constants


# Create your views here.
def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def populate_stake_holders(request):
    new_stake_holders = _fetch_stake_holders()
    new_stake_holder_addresses = [holder.address for holder in new_stake_holders]
    existing_stake_holders = _load_stake_holders()
    if len(new_stake_holder_addresses) != 0:
        filtered = [holder for holder in existing_stake_holders if holder.address not in new_stake_holder_addresses]
        for filtered_holder in filtered:
            filtered_holder.receiving_reward = False
            filtered_holder.save()
    for new_holder in new_stake_holders:
        new_holder.save()
    return HttpResponse("success")


def _fetch_stake_holders():
    r = requests.get('https://explorerapi.masscafe.cn/v1/explorer/transactions/staking/reward/top/?limit=30')
    data_set = r.json()['data']
    timestamp = datetime.timestamp(datetime.now())
    new_stake_holders = [_data_to_stake_holder(data, timestamp) for data in data_set]
    return new_stake_holders


def _data_to_stake_holder(data, timestamp):
    return StakeHolder(address=data['address'], total_amount=data['total_amount'],
                       order=data['id'], timestamp=timestamp, receiving_reward=True)


def get_stake_holders(request):
    stake_holder_view_models = sorted(_get_stake_holder_view_model_dic(), key=lambda vm: vm.current_rank())
    total = reduce(lambda accu, result: accu + float(result.current_total_amount()), stake_holder_view_models, 0)
    transaction_view_models = [TransactionViewModel(tx) for tx in _load_transactions()]
    tx_sum_list = _generate_grouped_transactions(transaction_view_models)
    sorted_transaction_view_models = sorted(transaction_view_models, key=lambda tx: tx.timestamp)

    context = {
        'stake_holders': stake_holder_view_models,
        'transactions': sorted_transaction_view_models,
        'sum': tx_sum_list,
        'total': total
    }
    return render(request, 'staking/index.html', context)


def get_stake_holders_with_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="holder_summary.csv"'

    stake_holder_view_models = sorted(_get_stake_holder_view_model_dic(), key=lambda vm: vm.current_rank())

    writer = csv.writer(response)
    writer.writerow(['Address', 'Rank', 'Change since yesterday', 'Total amount', 'Change since yesterday'])
    for holder in stake_holder_view_models:
        writer.writerow([holder.address, holder.current_rank(), holder.rank_change(),
                         holder.current_total_amount(), holder.amount_change()])

    return response


def get_transactions_with_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="holder_transactions.csv"'

    transaction_view_models = [TransactionViewModel(tx) for tx in _load_transactions()]
    sorted_transaction_view_models = sorted(transaction_view_models, key=lambda tx: tx.timestamp)

    writer = csv.writer(response)
    writer.writerow(['Address', 'Transaction Amount', 'Locking Time', 'Unlocking Time'])
    for tx in sorted_transaction_view_models:
        writer.writerow([tx.holder_address, tx.total, tx.locking_time, tx.unlocking_time])

    return response


def _generate_grouped_transactions(transaction_view_models):
    sorted_transaction_view_models = sorted(transaction_view_models, key=lambda tx: tx.timestamp)
    data_frame = pandas.DataFrame.from_records([vars(vm) for vm in sorted_transaction_view_models])
    tx_sum = data_frame.groupby('unlocking_day')['total'].sum()
    dic = tx_sum.to_dict()
    tx_sum_list = [{'date': tx.to_pydatetime().date, 'value': dic[tx]} for tx in dic]
    return tx_sum_list


def _load_transactions():
    now = datetime.now()
    locking_timestamp = datetime.timestamp(datetime(year=now.year,
                                                    month=now.month,
                                                    day=now.day)) - 61440 * 45
    all_transactions = Transaction.objects.filter(amount__gt=0, timestamp__gte=locking_timestamp)
    return [tx for tx in all_transactions if tx.holder_address not in Constants.official_addresses]


def populate_transactions(request):
    stake_holder_view_model_dic = _get_stake_holder_view_model_dic()
    for vm in stake_holder_view_model_dic:
        address = vm.address
        if round(vm.amount_change(), 0) != 0:
            print('populate transactions for address: %s' % address)
            url = ('https://explorerapi.masscafe.cn/v1/explorer/addresses/%s/?page=1&tx_type=1' % address)
            transactions = _fetch_transactions_from(address, url, single_page_only=(len(vm.holders) > 1))
            for transaction in transactions:
                transaction.save()
    return HttpResponse()


def _get_stake_holder_view_model_dic():
    stake_holders = _load_stake_holders()
    holders_dic = {}
    for holder in stake_holders:
        vm = holders_dic.get(holder.address)
        if vm is None:
            holders_dic[holder.address] = StakingViewModel(holder)
        else:
            holders_dic.get(holder.address).add_holder(holder)
    return holders_dic.values()


def _load_stake_holders():
    stake_holders = StakeHolder.objects.filter(receiving_reward=True)
    return [holder for holder in stake_holders if holder.address not in Constants.official_addresses]


def _fetch_transactions_from(address, url, single_page_only=False):
    print('fetching data from url: %s' % url)
    json = requests.get(url).json()
    transaction_list = requests.get(url).json()['results']['data']['transaction_list']
    transactions = [_map_data_to_transaction(address, data) for data in transaction_list]

    if (not single_page_only) and (json['next'] is not None):
        transactions.extend(_fetch_transactions_from(address, json['next']))
    return transactions


def _map_data_to_transaction(address, data):
    transaction = Transaction(hash=data['txhash'], amount=data['collect'],
                              timestamp=data['tx']['block']['timestamp'], holder_address=address)
    return transaction
