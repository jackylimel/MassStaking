from datetime import datetime

from pytz import timezone


class StakingViewModel:

    def __init__(self, holder):
        self.address = holder.address
        self.transactions = []
        self.holders = []
        self.holders.append(holder)

    def add_holder(self, holder):
        self.holders.append(holder)
        self.holders.sort(key=lambda h: h.timestamp, reverse=True)

    def is_new_holder(self):
        return len(self.holders) == 1

    def current_rank(self):
        return self._top_holder().order

    def current_total_amount(self):
        return self._top_holder().total_amount

    def current_timestamp(self):
        return self._top_holder().timestamp

    def rank_change(self):
        if len(self.holders) >= 2:
            return self.holders[1].order - self._top_holder().order
        else:
            return self._top_holder().order

    def amount_change(self):
        if len(self.holders) >= 2:
            return round(self._top_holder().total_amount - self.holders[1].total_amount, 1)
        else:
            return self._top_holder().total_amount

    def _top_holder(self):
        return self.holders[0]


class TransactionViewModel:
    def __init__(self, transaction):
        self.total = transaction.amount
        self.timestamp = transaction.timestamp
        self.holder_address = transaction.holder_address
        self.locking_time = DateHelper.from_time_stamp(transaction.timestamp)
        if self.total > 0:
            self.unlocking_time = DateHelper.from_time_stamp(
                float(transaction.timestamp) + 61440 * 45 - 3600 * 24 * 2 - 3600 * 17)
            self.unlocking_day = datetime(year=self.unlocking_time.year,
                                          month=self.unlocking_time.month,
                                          day=self.unlocking_time.day)
        else:
            self.unlocking_time = None
            self.unlocking_day = None


class BindingViewModel:
    def __init__(self):
        self.bindings = []

    def add_binding(self, binding):
        self.bindings.append(binding)
        self.bindings.sort(key=lambda b: b.timestamp, reverse=True)

    def amount_change(self):
        if len(self.bindings) >= 2:
            return self._top_binding().amount - self.bindings[1].amount
        else:
            return self._top_binding().amount

    def current_total_amount(self):
        return self._top_binding().amount

    def current_timestamp(self):
        return self._top_binding().timestamp

    def _top_binding(self):
        return self.bindings[0]


class DateHelper:
    @staticmethod
    def from_time_stamp(timestamp):
        tz = timezone('Asia/Chongqing')
        return datetime.fromtimestamp(float(timestamp), tz)
