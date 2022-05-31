import datetime


def year(request):
    return {'year': str((datetime.datetime.now()))[:4]}

def time(request):
    return {'time': str((datetime.datetime.now().strftime("%H:%M:%S")))}
