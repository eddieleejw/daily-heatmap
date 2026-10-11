from datetime import date, timedelta


def list_dates(start_date: date, end_date: date) -> list[date]:

    delta = end_date - start_date

    return [start_date + timedelta(days=i) for i in range(delta.days + 1)]