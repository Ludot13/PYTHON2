from datetime import datetime


def year(request):
    today_year = datetime.now().year
    return {
        'year': today_year
    }
