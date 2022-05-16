import datetime


def year(request):
    return {'year': str((datetime.datetime.now()))[:4]}
