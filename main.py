# -*- coding: utf-8 -*-

import os
import time
from http import cookiejar
from datetime import datetime, timedelta, timezone

import requests
from pyquery import PyQuery as pq

import config as cf

PACKT_URL = "https://www.packtpub.com"

SAVE_DIR = os.path.join(os.getcwd(), 'eBooks')

headers = {
    "Host": "www.packtpub.com",
    "Origin": PACKT_URL,
    "Referer": PACKT_URL,
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"
}

session = requests.session()
session.cookies = cookiejar.LWPCookieJar(filename='cookies.txt')
try:
    print("Trying to load cookies...")
    session.cookies.load(ignore_discard=True)
except:
    print("Load cookies failed!")


def get_save_dir(name=None):
    pass


def get_time_now():
    tz_utc_8 = timezone(timedelta(hours=8))
    now = datetime.now()
    dt = now.replace(tzinfo=tz_utc_8)
    dt_str = dt.strftime('%Y-%m-%d %H:%M:%S')
    return dt_str


def get_form_build_id():
    response = session.get(PACKT_URL, headers=headers)
    doc = pq(response.content)
    form_build_id = doc('input:hidden[name="form_build_id"]').val()
    return form_build_id


def login(email, password, op, form_id):
    print("Login...")
    data = {
        'email': email,
        'password': password,
        'op': op,
        'form_build_id': get_form_build_id(),
        'form_id': form_id
    }
    response = session.post(PACKT_URL, data=data, headers=headers)
    if response.status_code == 200:
        session.cookies.save()
        print("Login successed!")
    else:
        print("Login faild!")


def get_free_ebook():
    free_url = "https://www.packtpub.com/packt/offers/free-learning"
    response = session.get(free_url, headers=headers)

    doc = pq(response.content)
    name = doc(".dotd-title > h2").text()
    claim_url = PACKT_URL + doc('.free-ebook > a').attr("href")
    print(name)
    response = session.get(claim_url, headers=headers)

    if response.status_code == 200:
        session.cookies.save()
        print("========== Finished at {0} ==========".format(get_time_now()))
    else:
        login(cf.account['email'], cf.account['password'], cf.op, cf.form_id)
        get_free_ebook()


def store_ebooks():
    ebooks_url = "https://www.packtpub.com/account/my-ebooks"
    response = session.get(ebooks_url, headers=headers)

    if response.status_code == 200:
        session.cookies.save()

        doc = pq(response.content)
        book_list = doc('#product-account-list .product-line')
        # TODO: Save books
    else:
        login(cf.account['email'], cf.account['password'], cf.op, cf.form_id)
        store_ebooks()


def auto_claim():
    while True:
        print("Start...")
        get_free_ebook()
        print("Sleep...")
        time.sleep(28800)


if __name__ == '__main__':
    options = {
        '0': quit,
        '1': get_free_ebook,
        '3': auto_claim
    }
    step = input(
        """Choose an option:\n
        1. Claim today's free ebook\n
        2. Save your ebooks\n
        3. Auto claim free ebooks\n
        0. Quit\n
        Your choice: """)
    options[step]()
