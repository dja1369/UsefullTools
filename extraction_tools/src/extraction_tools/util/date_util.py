from datetime import datetime, timedelta
from itertools import groupby


class DateUtil:
    def search_all_date(self, start: datetime, end: datetime):
        """
        입력한 날짜 사이의 모든 기간을 반환
        """
        date_range = [ (start + timedelta(days = date)).date() for date in range((end - start).days + 1)]
        date_range.sort(reverse=True)
        date_group = groupby(date_range, key = lambda x: (x.year, x.month))
        result = { "-".join(map(str,key)): list(group) for key, group in date_group}
        return result

