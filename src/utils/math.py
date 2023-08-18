def median(numbers: 'List[int]') -> int:
    sorted_numbers = sorted(numbers)
    length = len(numbers)
    index = (length - 1) // 2

    if length % 2:
        return sorted_numbers[index]
    else:
        return int((sorted_numbers[index] + sorted_numbers[index + 1]) / 2.0)


def mean(numbers: 'List[int]') -> int:
    return int(sum(numbers) / len(numbers))
