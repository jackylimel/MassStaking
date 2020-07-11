import csv
from functools import reduce

from django.http import HttpResponse

from ..services import *
from ..view_models import *


def populate_stake_holders(request):
    timestamp = datetime.timestamp(datetime.now())
    update_total_staking(timestamp)
    print("updating binding")
    update_binding(timestamp)
    print('updating stake holders')
    new_stake_holders = fetch_stake_holders(timestamp)
    new_stake_holder_addresses = [holder.address for holder in new_stake_holders]
    existing_stake_holders = load_stake_holders()
    if len(new_stake_holder_addresses) != 0:
        filtered = [holder for holder in existing_stake_holders if holder.address not in new_stake_holder_addresses]
        for filtered_holder in filtered:
            filtered_holder.receiving_reward = False
            filtered_holder.save()
    for new_holder in new_stake_holders:
        new_holder.save()
    return calculate_unstaking_transactions(timestamp)


def calculate_unstaking_transactions(timestamp):
    print("updating block height")
    update_block_height(timestamp)

    current, future, seconds_per_block = get_current_and_future_block()
    min_staking_height = current - 61440
    max_staking_height = future - 61440
    transactions = load_transactions_between(min_staking_height, max_staking_height)
    transaction_view_models = [TransactionViewModel(tx) for tx in transactions]
    sorted_transaction_view_models = sorted(transaction_view_models, key=lambda tx: tx.timestamp)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="holder_transactions.csv"'
    writer = csv.writer(response)
    writer.writerow(['----------------------------------------'])
    writer.writerow(['当前区块高度', '出`块时间(秒)'])
    writer.writerow([current, int(seconds_per_block)])
    writer.writerow(['----------------------------------------'])
    writer.writerow(['地址', '解锁金额', '锁仓区块', '解锁区块'])
    for tx in sorted_transaction_view_models:
        writer.writerow([tx.holder_address, tx.total, tx.locking_block, tx.unlocking_block])
    return response


def populate_transactions(request):
    for address in load_distinct_stake_holder_addresses():
        print('populate transactions for address: %s' % address)
        url = ('https://explorerapi.masscafe.cn/v1/explorer/addresses/%s/?page=1&tx_type=1' % address)
        existing_hashes = load_transaction_hashes_for_address(address)
        fetch_transactions_from(address, url, existing_hashes)
    return get_stake_holders_with_csv()


def get_stake_holders_with_csv():
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="holder_summary.csv"'

    stake_holder_view_models = sorted(_get_stake_holder_view_model_dic(), key=lambda vm: vm.current_rank())

    writer = csv.writer(response)

    writer.writerow(['Total Binding', 'Change since yesterday'])
    binding_view_model = _get_binding_view_model()
    writer.writerow([binding_view_model.current_total_amount(), binding_view_model.amount_change()])
    writer.writerow(['----------------------------------------'])

    writer.writerow(['Top 30 Staking', 'Change since yesterday'])
    top_30_staking = reduce(lambda accu, result: accu + result.current_total_amount(), stake_holder_view_models, 0)
    top_30_staking_change = reduce(lambda accu, result: accu + result.amount_change(), stake_holder_view_models, 0)
    writer.writerow([top_30_staking, top_30_staking_change])
    writer.writerow(['----------------------------------------'])

    writer.writerow(['Total Staking', 'Change since yesterday'])
    total_staking_view_model = _get_total_staking_view_model()
    writer.writerow([total_staking_view_model.current_total_amount(), total_staking_view_model.amount_change()])
    writer.writerow(['----------------------------------------'])

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


def _get_binding_view_model():
    view_model = BindingViewModel()
    for binding in load_bindings():
        view_model.add_binding(binding)
    return view_model


def _get_total_staking_view_model():
    view_model = BindingViewModel()
    for staking in load_total_staking():
        view_model.add_binding(staking)
    return view_model
