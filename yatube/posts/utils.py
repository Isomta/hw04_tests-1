from django.core.paginator import Paginator

from yatube.settings import CUT_LENGTH as CL


def func_paginator(request, pag):
    paginator = Paginator(pag, CL)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
