from datetime import datetime

import requests

from .constants import Constants
from .models import *


def fetch_stake_holders():
    r = requests.get('https://explorerapi.masscafe.cn/v1/explorer/transactions/staking/reward/top/?limit=30')
    data_set = r.json()['data']
    timestamp = datetime.timestamp(datetime.now())
    new_stake_holders = [_data_to_stake_holder(data, timestamp) for data in data_set]
    return new_stake_holders


def _data_to_stake_holder(data, timestamp):
    return Holder(address=data['address'], total_amount=data['total_amount'],
                  order=data['id'], timestamp=timestamp, receiving_reward=True, type=StakeHolderType.STAKING.value)


def fetch_transactions_from(address, url, single_page_only=False):
    print('fetching data from url: %s' % url)
    json = requests.get(url).json()
    transaction_list = json['results']['data']['transaction_list']
    transactions = [_map_data_to_transaction(address, data) for data in transaction_list]

    if (not single_page_only) and (json['next'] is not None):
        transactions.extend(fetch_transactions_from(address, json['next']))
    return transactions


def _map_data_to_transaction(address, data):
    transaction = Transaction(hash=data['txhash'], amount=data['collect'],
                              timestamp=data['tx']['block']['timestamp'], holder_address=address)
    return transaction


def load_stake_holders():
    stake_holders = Holder.objects.filter(receiving_reward=True, type=StakeHolderType.STAKING.value)
    return [holder for holder in stake_holders if holder.address not in Constants.official_addresses]


def load_transactions():
    now = datetime.now()
    locking_timestamp = datetime.timestamp(datetime(year=now.year,
                                                    month=now.month,
                                                    day=now.day)) - 61440 * 45
    all_transactions = Transaction.objects.filter(amount__gt=0, timestamp__gte=locking_timestamp)
    return [tx for tx in all_transactions if tx.holder_address not in Constants.official_addresses]


def update_exchange_addresses():
    timestamp = datetime.timestamp(datetime.now())

    for address in Constants.exchange_address.keys():
        r = requests.get('https://explorerapi.masscafe.cn/v1/explorer/addresses/%s' % address)
        data = r.json()['results']['data']
        holder = Holder(address=address, total_amount=data['balance'], order=999, timestamp=timestamp,
                        receiving_reward=False, type=StakeHolderType.EXCHANGE.value)
        holder.save()
