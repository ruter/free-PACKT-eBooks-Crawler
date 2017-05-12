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


def get_save_path(name=None):
    save_path = os.path.join(SAVE_DIR, name)
    return save_path


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
    print("Claim {0} now...".format(name))
    response = session.get(claim_url, headers=headers)

    if response.status_code == 200:
        session.cookies.save()
        print("========== Finished at {0} ==========".format(get_time_now()))
    else:
        login(cf.account['email'], cf.account['password'], cf.op, cf.form_id)
        get_free_ebook()


def download_ebook(url=None):
    try:
        res = session.get(url, headers=headers, allow_redirects = False)
        dl_url = res.headers['Location']
        res = session.get(dl_url, stream=True)
        if res.status_code == 200:
            return res
    except Exception as e:
        print("Download failed: [{0}]".format(e))


def save_ebooks():
    if not os.path.exists(SAVE_DIR):
        os.mkdir(SAVE_DIR)

    print("Start download your eBooks...")

    ebooks_url = "https://www.packtpub.com/account/my-ebooks"
    response = session.get(ebooks_url, headers=headers)

    if response.status_code == 200:
        session.cookies.save()

        doc = pq(response.content)
        book_list = doc('#product-account-list .product-line')
        for book in book_list:
            book = pq(book)
            try:
                name = book.attr('title').rstrip(' [eBook]')
            except:
                name = book.attr('title')
            
            save_dir = get_save_path(name)
            if os.path.exists(save_dir):
                print("{0} already existed!".format(name))
            else:
                os.mkdir(save_dir)
                save_path = os.path.join(save_dir, "{0}.pdf".format(name))
                url = PACKT_URL + book.find('.product-buttons-line .download-container').eq(1).children('a').attr(
                    'href')
                pdf = download_ebook(url)
                try:
                    with open(save_path, 'wb') as f:
                        for chunk in pdf.iter_content(chunk_size=1024):
                            if chunk:
                                f.write(chunk)
                                f.flush()
                    print("{0} has been saved!\nTrying next...".format(name))
                except Exception as e:
                    print("Save error: [{0}] trying next...".format(e))
    else:
        login(cf.account['email'], cf.account['password'], cf.op, cf.form_id)
        save_ebooks()


def auto_claim():
    while True:
        print("Start...")
        get_free_ebook()
        print("Sleep...")
        time.sleep(cf.frequency * 3600)


if __name__ == '__main__':
    options = {
        '0': quit,
        '1': get_free_ebook,
        '2': save_ebooks,
        '3': auto_claim
    }
    step = input(
        """Choose an option:\n
        1. Claim today's free ebook\n
        2. Download all your ebooks\n
        3. Auto claim free ebooks\n
        0. Quit\n
        Your choice: """)
    options[step]()
