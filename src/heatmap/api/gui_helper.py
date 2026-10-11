from typing import List


def process_weeks(weeks: List[int]) -> List[List[int]]:
    '''
    Takes a list of days and processes it to remove any non-leading 0s, and return it partitioned by weeks

    e.g. [0, 0, 0, 1, 2, 3, 4, 5, ..., 30, 31, 0, 0, 0, 1, 2, ...] -> [[0, 0, 0, 1, 2, 3, 4], [5, 6, ...], ..., [..., 30, 31, 1, ...], ...]

    '''
    first_week = True

    removed_zeros = []

    for day in weeks:
        if day == 0 and first_week:
            removed_zeros.append(day)
        elif day == 0 and not first_week:
            continue
        else:
            first_week = False
            removed_zeros.append(day)

    removed_zeros += [0 for _ in range((7 - (len(removed_zeros) % 7))%7)]

    return [[removed_zeros[i + 7*weeks] for i in range(7)] for weeks in range(len(removed_zeros)//7)]