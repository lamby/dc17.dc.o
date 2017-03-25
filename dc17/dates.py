import datetime


def meals(orga=False):
    day = datetime.date(2017, 7, 31)
    if orga:
        day = datetime.date(2017, 7, 28)
    while day <= datetime.date(2017, 8, 13):
        yield ('breakfast', day)
        if day < datetime.date(2017, 8, 13):
            yield ('lunch', day)
            yield ('dinner', day)
        day += datetime.timedelta(days=1)


def meal_choices(orga=False):
    for meal, date in meals(orga=orga):
        date = date.isoformat()
        yield ('{}_{}'.format(meal, date),
               '{} {}'.format(meal.title(), date))


def nights(orga=False):
    day = datetime.date(2016, 7, 31)
    if orga:
        day = datetime.date(2016, 7, 28)
    while day <= datetime.date(2016, 8, 13):
        yield day
        day += datetime.timedelta(days=1)


def night_choices(orga=False):
    for date in nights(orga=orga):
        date = date.isoformat()
        yield ('night_{}'.format(date), 'Night of {}'.format(date))
