import csv

import pandas
from django.http import HttpResponse

from .services import *
from .view_models import *


def populate_stake_holders(request):
    new_stake_holders = fetch_stake_holders()
    new_stake_holder_addresses = [holder.address for holder in new_stake_holders]
    existing_stake_holders = load_stake_holders()
    if len(new_stake_holder_addresses) != 0:
        filtered = [holder for holder in existing_stake_holders if holder.address not in new_stake_holder_addresses]
        for filtered_holder in filtered:
            filtered_holder.receiving_reward = False
            filtered_holder.save()
    for new_holder in new_stake_holders:
        new_holder.save()
    return HttpResponse("success")


def populate_transactions(request):
    for vm in _get_stake_holder_view_model_dic():
        address = vm.address
        if round(vm.amount_change(), 0) != 0:
            print('populate transactions for address: %s' % address)
            url = ('https://explorerapi.masscafe.cn/v1/explorer/addresses/%s/?page=1&tx_type=1' % address)
            transactions = fetch_transactions_from(address, url, single_page_only=(len(vm.holders) > 1))
            for transaction in transactions:
                transaction.save()
    return HttpResponse()


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


def _get_stake_holder_view_model_dic():
    stake_holders = load_stake_holders()
    holders_dic = {}
    for holder in stake_holders:
        vm = holders_dic.get(holder.address)
        if vm is None:
            holders_dic[holder.address] = StakingViewModel(holder)
        else:
            holders_dic.get(holder.address).add_holder(holder)
    return holders_dic.values()


def get_transactions_with_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="holder_transactions.csv"'

    transaction_view_models = [TransactionViewModel(tx) for tx in load_transactions()]
    sorted_transaction_view_models = sorted(transaction_view_models, key=lambda tx: tx.timestamp)

    writer = csv.writer(response)
    writer.writerow(['Address', 'Transaction Amount', 'Locking Time', 'Unlocking Time'])
    for tx in sorted_transaction_view_models:
        writer.writerow([tx.holder_address, tx.total, tx.locking_time, tx.unlocking_time])

    return response


def get_transaction_sum_with_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sum.csv"'
    transaction_view_models = [TransactionViewModel(tx) for tx in load_transactions()]
    tx_sum_list = _generate_grouped_transactions(transaction_view_models)
    writer = csv.writer(response)
    writer.writerow(['Unlocking Time', 'Total'])
    for tx in tx_sum_list:
        writer.writerow([tx['date'].date(), round(tx['value'], 0)])

    return response


def _generate_grouped_transactions(transaction_view_models):
    sorted_transaction_view_models = sorted(transaction_view_models, key=lambda tx: tx.timestamp)
    data_frame = pandas.DataFrame.from_records([vars(vm) for vm in sorted_transaction_view_models])
    tx_sum = data_frame.groupby('unlocking_day')['total'].sum()
    dic = tx_sum.to_dict()
    tx_sum_list = [{'date': tx.to_pydatetime(), 'value': round(dic[tx], 0)} for tx in dic]
    return tx_sum_list
