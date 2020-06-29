from django.http import HttpResponse
import pandas

from ..services import *


def populate_transactions(request):
    for address in load_distinct_stake_holder_addresses():
        print('populate transactions for address: %s' % address)
        url = ('https://explorerapi.masscafe.cn/v1/explorer/addresses/%s/?page=1&tx_type=1' % address)
        existing_hashes = load_transaction_hashes_for_address(address)
        fetch_transactions_from(address, url, existing_hashes)
    return HttpResponse()

# def get_transactions_with_csv(request):
#     response = HttpResponse(content_type='text/csv')
#     response['Content-Disposition'] = 'attachment; filename="holder_transactions.csv"'
#
#     transaction_view_models = [TransactionViewModel(tx) for tx in load_transactions()]
#     sorted_transaction_view_models = sorted(transaction_view_models, key=lambda tx: tx.timestamp)
#
#     writer = csv.writer(response)
#     writer.writerow(['Address', 'Transaction Amount', 'Locking Time', 'Unlocking Time'])
#     for tx in sorted_transaction_view_models:
#         writer.writerow([tx.holder_address, tx.total, tx.locking_time, tx.unlocking_time])
#
#     return response


# def get_transaction_sum_with_csv(request):
#     response = HttpResponse(content_type='text/csv')
#     response['Content-Disposition'] = 'attachment; filename="sum.csv"'
#     transaction_view_models = [TransactionViewModel(tx) for tx in load_transactions()]
#     tx_sum_list = _generate_grouped_transactions(transaction_view_models)
#     writer = csv.writer(response)
#     writer.writerow(['Unlocking Time', 'Total'])
#     for tx in tx_sum_list:
#         writer.writerow([tx['date'].date(), round(tx['value'], 0)])
#
#     return response


# def _generate_grouped_transactions(transaction_view_models):
#     sorted_transaction_view_models = sorted(transaction_view_models, key=lambda tx: tx.timestamp)
#     data_frame = pandas.DataFrame.from_records([vars(vm) for vm in sorted_transaction_view_models])
#     tx_sum = data_frame.groupby('unlocking_day')['total'].sum()
#     dic = tx_sum.to_dict()
#     tx_sum_list = [{'date': tx.to_pydatetime(), 'value': round(dic[tx], 0)} for tx in dic]
#     return tx_sum_list
