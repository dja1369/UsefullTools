from datetime import datetime, timedelta, date
from itertools import groupby


class DateUtil:
    def search_all_date(self, start: datetime, end: datetime) -> dict[str, list[date]]:
        """
        입력한 날짜 사이의 모든 기간을 반환
        :return : { "year-month": [date, date, ...], ...}
        """
        date_range = [ (start + timedelta(days = date)).date() for date in range((end - start).days + 1)]
        date_range.sort(reverse=True)
        date_group = groupby(date_range, key = lambda x: (x.year, x.month))
        result = { "-".join(map(str,key)): list(group) for key, group in date_group}
        return result

