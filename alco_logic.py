import datetime
import locale

from services import get_right_ending

locale.setlocale(locale.LC_ALL, "ru_RU")


def next_drink_day(last_drank=None, current_penalty=None):
    if last_drank:
        datetime_object = datetime.datetime.strptime(last_drank, "%Y-%m-%d %H:%M:%S.%f")

        next_day = datetime_object + datetime.timedelta(days=current_penalty)
        return next_day.strftime("%-d %-B после %H:%M")
    return None


def drink_timer(last_drank):
    if last_drank is None:
        return None, True

    datetime_object = datetime.datetime.strptime(last_drank, "%Y-%m-%d %H:%M:%S.%f")

    if datetime.datetime.now() - datetime_object < datetime.timedelta(hours=24):
        time_diff = (
            datetime_object + datetime.timedelta(days=1) - datetime.datetime.now()
        )
        clear_time = get_right_ending(timedelta=time_diff)
        return clear_time, False

    time_diff = datetime.datetime.now() - datetime_object
    clear_time = get_right_ending(days=time_diff)

    return clear_time, True
