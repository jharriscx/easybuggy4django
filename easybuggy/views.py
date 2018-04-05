import time
import os
import psutil
import sys

from time import sleep
from django.db import transaction
from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _

from .models import User


a = []


def index(request):
    d = {'title': 'EasyBuggy Django'}
    return render(request, 'index.html', d)


def deadlock2(request):
    d = {
        'title': _('title.deadlock2.page'),
        'note': _('msg.note.deadlock2'),
    }
    order = getOrder(request)
    if request.method == 'POST':
        with transaction.atomic():
            number = 0
            while True:
                number += 1
                uid = request.POST.get("uid_" + str(number))
                if uid is None:
                    break
                user = User.objects.get(id=uid)
                user.name = request.POST.get(uid + "_name")
                user.phone = request.POST.get(uid + "_phone")
                user.mail = request.POST.get(uid + "_mail")
                user.save()
                sleep(1)

    d['users'] = User.objects.raw("SELECT * FROM easybuggy_user WHERE ispublic = 'true' ORDER BY id " + order)
    d['order'] = order
    return render(request, 'deadlock2.html', d)


def infiniteloop(request):
    i = 1
    while 0 < i:
        i += 1



def redirectloop(request):
    return redirect("/redirectloop")


def infiniteloop(request):
    i = 1
    while 0 < i:
        i += 1


def memoryleak(request):
    leakMemory()
    d = {
        'title': _('title.memoryleak.page'),
        'note': _('msg.note.memoryleak'),
    }
    try:
        ps = psutil.Process(os.getpid())
        mem = ps.memory_full_info()
        d = {
            'title': _('title.memoryleak.page'),
            'note': _('msg.note.memoryleak'),
            'pid': ps.pid,
            'rss': convert_bytes(mem.rss),
            'pcnt_rss': round(ps.memory_percent(memtype='rss') ,2),
            # 'vms': mem.vms,
            # 'shared': mem.shared,
            # 'text': mem.text,
            # 'lib': mem.lib,
            # 'data': mem.data,
            # 'dirty': mem.dirty,
            'uss': convert_bytes(mem.uss),
            'pcnt_uss': round(ps.memory_percent(memtype='uss') ,2),
            'pss': convert_bytes(mem.pss),
            'pcnt_pss': round(ps.memory_percent(memtype='pss') ,2),
            'swap': convert_bytes(mem.swap),
            'info': ps.as_dict(attrs=["cmdline", "username"]),
        }
    except psutil.AccessDenied:
        pass
    except psutil.NoSuchProcess:
        pass
    return render(request, 'memoryleak.html', d)

def roe(request):
    d = {
        'title': _('title.roundofferror.page'),
        'note': _('msg.note.roundofferror'),
    }
    if request.method == 'POST':
        number = request.POST["number"]
        d['number'] = number
        if number is not None and number is not "0" and number.isdigit():
            d['result'] = float(number) - 0.9
    return render(request, 'roundofferror.html', d)


def te(request):
    d = {
        'title': _('title.truncationerror.page'),
        'note': _('msg.note.truncationerror'),
    }
    if request.method == 'POST':
        number = request.POST["number"]
        d['number'] = number
        if number is not None and number is not "0" and number.isdigit():
            d['result'] = 10.0 / float(number)
    return render(request, 'truncationerror.html', d)


def xss(request):
    d = {
        'title': _('title.xss.page'),
        'msg': _('msg.enter.string'),
        'note': _('msg.note.xss'),
    }
    if request.method == 'POST':
        str = request.POST["string"]
        if str is not None:
            d['msg'] = str[::-1]

    return render(request, 'xss.html', d)


def sqlijc(request):
    d = {
        'title': _('title.sqlijc.page'),
        'note': _('msg.note.sqlijc'),
    }
    if request.method == 'POST':
        name = request.POST["name"]
        password = request.POST["password"]
        d['users'] = User.objects.raw("SELECT * FROM easybuggy_user WHERE ispublic = 'true' AND name='" + name +
                                      "' AND password='" + password + "' ORDER BY id")

    return render(request, 'sqlijc.html', d)


# -------- private method
def getOrder(request):
    order = request.GET.get("order")
    if order == 'asc':
        order = 'desc'
    else:
        order = 'asc'
    return order


def leakMemory():
    global a
    for i in range(100000):
        a.append(time.time())


def convert_bytes(n):
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.1f%s' % (value, s)
    return "%sB" % n