from datetime import datetime

from pytz import timezone


class StakingViewModel:

    def __init__(self, holder):
        self.address = holder.address
        self.total = holder.total_amount
        self.time = DateHelper.from_time_stamp(holder.timestamp)
        self.rank = holder.order
        self.transactions = []

    def add_transactions(self, transactions):
        self.transactions.extend(sorted(transactions, key=lambda tx: tx.timestamp))


class TransactionViewModel:
    def __init__(self, transaction):
        self.total = transaction.amount
        self.timestamp = transaction.timestamp
        self.holder_address = transaction.holder_address
        self.locking_time = DateHelper.from_time_stamp(transaction.timestamp)
        if self.total > 0:
            self.unlocking_time = DateHelper.from_time_stamp(float(transaction.timestamp) + 61440 * 45)
        else:
            self.unlocking_time = None


class DateHelper:
    @staticmethod
    def from_time_stamp(timestamp):
        tz = timezone('Asia/Chongqing')
        return datetime.fromtimestamp(float(timestamp), tz)
