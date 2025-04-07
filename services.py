"""
Помощь боту в склонении слов
"""


def get_right_ending(timedelta=None, days=None):
    clear_time = ""
    if timedelta:
        parsed = str(timedelta).split(":")[:2]  # [:2] вытаскивает часы и минуты
        hours, minutes = parsed[0], parsed[1]
        units = int(hours) % 10
        tens = (int(hours) // 10) % 10

        if tens == 1 or units in [0, 5, 6, 7, 8, 9]:
            clear_time += f"{tens}{units} часов"
        elif units in [2, 3, 4]:
            clear_time += f"{tens}{units} часа"
        else:
            clear_time += f"{tens}{units} час"

        units = int(minutes) % 10
        tens = (int(minutes) // 10) % 10

        if tens == 1 or units in [0, 5, 6, 7, 8, 9]:
            clear_time += f" {tens}{units} минут"
        elif units in [2, 3, 4]:
            clear_time += f" {tens}{units} минуты"
        else:
            clear_time += f" {tens}{units} минута"

    elif days:
        parsed = int(str(days).split()[0])  # вытаскиваем дни из datetime object
        units = parsed % 10
        tens = (parsed // 10) % 10

        if tens == 1 or units in [0, 5, 6, 7, 8, 9]:
            clear_time += f"{tens}{units} дней"
        elif units in [2, 3, 4]:
            clear_time += f"{tens}{units} дня"
        else:
            clear_time += f"{tens}{units} день"

    no_zeroes = ""
    for _ in clear_time.split():
        if _.startswith("0"):
            _ = _[1:]
        no_zeroes += _ + " "

    no_zeroes = no_zeroes[:-1]

    return no_zeroes
