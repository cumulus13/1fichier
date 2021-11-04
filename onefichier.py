#!/usr/bin/env python2
#~*~*encode:utf-8*~*~
#~*~*encoding:utf-8*~*~
from __future__ import print_function
import os, sys
from unidecode import unidecode
import requests
from bs4 import BeautifulSoup as bs
import argparse
from make_colors import make_colors
from pydebugger.debug import debug
from configset import configset
import progressbar
if sys.platform == 'win32':
    from pyidm import IDMan
from pywget import wget
import clipboard
import re
import traceback
import time
import bitmath
from proxy_tester import proxy_tester
import warnings
warnings.filterwarnings("ignore")
if sys.version_info.major == 3:
    raw_input = input
    from urllib.parse import urlparse
else:
    from urlparse import urlparse
import ast
import json
from datetime import datetime
import size as Size
import inspect
if sys.platform == 'win32':
    import msvcrt as getch
else:
    from pygetch.getch import getch# GETCHAR as getch
    setattr(getch, 'getch', getch.GETCHAR)
try:
    from pause import pause
except:
    def pause():
        q = raw_input(make_colors("Enter to continue, or [q]uit or e[x]it to quit !", 'lw', 'r'))
        if q == 'q' or q == 'x' or q == 'quit' or q == 'exit':
            sys.exit()

os.environ.update({'PYTHONIOENCODING':'UTF-8'})

class onefichier(object):
    def __init__(self):
        super(onefichier, self)
        self.url = "https://1fichier.com/"
        self.configname = os.path.join(os.path.dirname(os.path.realpath(__file__)), '1fichier.ini')
        self.config = configset(self.configname)
        self.sess = requests.Session()
        self.logined = False

        self.prefix = '{variables.task} >> {variables.subtask}'
        self.variables =  {'task': '--', 'subtask': '--'}
        self.max_value = 10
        self.status_message = ""
        self.data = ''
        self.total = 0
        self.use_proxy = False
        self.proxies = []
        self.use_proxy_config = False
        self.use_proxy_config_download = False
        #self.use_proxy_proxies = False
        self.timeout = 60
        self.retries = 3
        self.sleep = 1
        self.bar = progressbar.ProgressBar(max_value = self.max_value, prefix = self.prefix, variables = self.variables, max_error = False)
        self.report = ''
        self.hidden_use_proxy_config = False
        self.hidden_use_proxy_download_config = False
        self.download_login = True
        self.max_try_replay = 2

    def set_header(self, header_str = None):
        """generate mediafire url to direct download url

        Args:
            header_str (str, optional): raw headers data/text from browser on development mode

        Returns:
            TYPE: dict: headers data
        """
        headers = {}
        if not header_str:
            header_str ="""accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
            accept-encoding: gzip, deflate
            accept-language: en-US,en;q=0.9,id;q=0.8,ru;q=0.7
            sec-fetch-dest: empty
            sec-fetch-mode: cors
            sec-fetch-site: same-origin
            sec-fetch-dest: document
            sec-fetch-user: ?1
            upgrade-insecure-requests: 1
            user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36"""

        debug(header_str = header_str)
        header_str = list(filter(None, re.split("\n|\r|\t\t", header_str)))
        debug(header_str = header_str)
        headers = {key.strip():value.strip() for key,value in [re.split(": |:\t", i) for i in header_str]}
        debug(headers = headers)
        return headers    

    def requests(self, *args, **kwargs):
        return self.request(*args, **kwargs)
    
    def request(self, url, rtype = 'get', headers = None, data = {}, params = {}, timeout = None, retries = None, sleep = None, proxies = {}):
        def browser(url, rtype, headers, data, params, timeout, retries, sleep, proxies = {}):
            n = 1
            error = False
            error_type = ''
            error_full = ''
            req = None
            #if not headers:
                #headers = self.set_header()
            if not "Mozilla" in self.sess.headers.get('user-agent'):# or not "mozilla" in headers.get('User-Agent'):
                headers1 = self.set_header()
                if headers1:
                    self.sess.headers.update(headers1)
            debug(headers = headers)
            debug(proxies = proxies)
            while 1:
                debug(url = url)
                debug(self_session_cookies = self.sess.cookies)
                try:
                    debug(self_session_cookies = self.sess.cookies.get_dict())
                except:
                    pass
                try:
                    debug(self_session_cookies = self.sess.cookies.get('SID'))
                except:
                    pass
                try:
                    if rtype == 'post':
                        if self.download_login:
                            req = self.sess.post(url, data=data, params = params, headers = headers, timeout = timeout, proxies = proxies)
                        else:
                            req = requests.post(url, data = data, headers = headers, timeout = timeout, proxies = proxies)
                    else:
                        if self.download_login:
                            req = self.sess.get(url, params = params, headers = headers, timeout = timeout, proxies = proxies)
                        else:
                            req = requests.get(url, params = params, headers = headers, timeout = timeout, proxies = proxies)
                    debug(req = req)
                    # break
                    return req, error, error_type, error_full
                except:
                    tr, vl, tb = sys.exc_info()
                    error_type = vl.__class__.__name__
                    debug(error_type = error_type)
                    error_full = traceback.format_exc()
                    debug(error_full = error_full)
                    debug(n = n)
                    debug(retries = retries)
                    if not n == retries or n < retries:
                        n += 1
                        debug(n = n)
                        if timeout < 60 and retries < 4:
                            debug(timeout = timeout)
                            timeout = timeout * n
                            debug(timeout = timeout)
                        time.sleep(sleep)
                    elif n > retries:
                        n == retries                    
                    else:
                        error = True
                        debug(error = error)
                        # #pause()
                        break
            debug(req = req)
            return req, error, error_type, error_full

        
        timeout = timeout or self.config.get_config('policy', 'timeout', '10') or self.timeout
        retries = retries or self.config.get_config('policy', 'retries', '3') or self.retries
        sleep = sleep or self.config.get_config('policy', 'sleep', '1') or self.sleep

        debug(timeout = timeout)
        debug(retries = retries)
        debug(sleep = sleep)
        proxies = self.build_proxy(proxies)
        debug(self_download_login = self.download_login)
        req, error, error_type, error_full = browser(url, rtype, headers, data, params, timeout, retries, sleep, proxies)
        exit = False
        while 1:
            debug(self_download_login = self.download_login)
            if error_type == 'ConnectionError' or error_type == 'ReadTimeout':
                qp = raw_input(make_colors("Connection Internet Error", 'lw', 'r') + ", " + make_colors("please check your internet connection !", 'ly') + ", " + make_colors("[n]t = retries with n times", 'b', 'lg') + ", " + make_colors("after that just enter or [q]quit or e[x]it for exit", 'lw', 'm') + ": ")
                if qp:
                    qp = qp.strip().lower()
                    if qp == 'x' or qp == 'exit' or qp == 'quit' or qp == 'q':
                        exit = True
                        break
                    elif qp[-1:] == 't' and qp[:-1].isdigit():
                        rn = int(qp[:-1])
                        for tr in range(rn + 1):
                            task = make_colors("re:Connection", 'lw', 'r')
                            subtask = make_colors("retry {}".format(tr), 'lw', 'm') + " "
                            self.bar.max_value = rn + 1
                            self.bar.update(tr, task = task, subtask = subtask)
                            req, error, error_type, error_full = browser(url, rtype, headers, data, params, timeout, retries, sleep)
                            if req:
                                subtask = make_colors("retry {} SUCCESS".format(tr), 'b', 'ly') + " "
                                self.bar.update(rn + 1, task = task, subtask = subtask)
                                break        
                            else:
                                subtask = make_colors("Failed".format(tr), 'lw', 'r') + " "
                                self.bar.update(rn + 1, task = task, subtask = subtask)
                else:
                    req, error, error_type, error_full = browser(url, rtype, headers, data, params, timeout, retries, sleep)
                    if req:
                        break
            else:
                break
        if exit:
            sys.exit()
        debug(req = req)
        
        if not req and proxies:
            debug("use proxies exists")
            #if isinstance(proxies, dict):
            print(make_colors("Use Proxy from dict", 'lw', 'r'))
            proxies = self.build_proxy(proxies)
            debug(proxies = proxies)
            if proxies.get('http'):
                print(make_colors("use http  list_proxy:", 'lw', 'm') + " " + make_colors(proxies.get('http'), 'lw', 'r'))
            if proxies.get('https'):
                print(make_colors("use https list_proxy:", 'lw', 'm') + " " + make_colors(proxies.get('https'), 'lw', 'r'))
            req, error, error_type, error_full = browser(url, rtype, headers, data, params, timeout, retries, sleep, proxies)
            
        if not req and (self.config.get_config('proxy', 'http') or self.config.get_config('proxy', 'https')):
            proxies_conf = {}
            print(make_colors("Use Proxy from config", 'lw', 'r'))
            if self.config.get_config('proxy', 'http'):
                proxies_conf = {
                    'http':'http://' + self.config.get_config('proxy', 'http'), 
                    'https':'https://' + self.config.get_config('proxy', 'http')
                }
            elif self.config.get_config('proxy', 'http'):
                proxies_conf = {'https':'https://' + self.config.get_config('proxy', 'http')}
            req, error, error_type, error_full = browser(url, rtype, headers, data, params, timeout, retries, sleep, proxies_conf)
            # if req:
            #     return req
            # else:
            if not req:
                self.config.write_config('proxy', 'http', '')
                self.config.write_config('proxy', 'https', '')
                self.use_proxy_config = False
            else:
                self.use_proxy_config = True

        if not req and (self.config.get_config('download_proxy', 'http') or self.config.get_config('download_proxy', 'https')):
            proxies_conf = {}
            print(make_colors("Use Proxy from config", 'lw', 'r'))
            if self.config.get_config('download_proxy', 'http'):
                proxies_conf = {
                    'http':'http://' + self.config.get_config('download_proxy', 'http'),
                    'https':'https://' + self.config.get_config('download_proxy', 'http'),
                }
            elif self.config.get_config('download_proxy', 'http'):
                proxies_conf = {'https':'https://' + self.config.get_config('download_proxy', 'http')}
            req, error, error_type, error_full = browser(url, rtype, headers, data, params, timeout, retries, sleep, proxies_conf)
            # if req:
            #     return req
            # else:
            if not req:
                self.config.write_config('proxy', 'http', '')
                self.config.write_config('proxy', 'https', '')
                self.use_proxy_config_download = False
            else:
                self.config.write_config('proxy', 'http', self.config.get_config('download_proxy', 'http'))
                self.config.write_config('proxy', 'https', self.config.get_config('download_proxy', 'https'))
                self.use_proxy_config_download = True

        if not req:
            if not self.proxies:
                pt = proxy_tester()
                list_proxy = pt.getProxyList()
                self.proxies = [i.get('ip') + ":" + i.get('port') for i in list_proxy]
                if proxies:
                    try:
                        self.proxies.remove(urlparse(proxies.get('http')).netloc)
                    except:
                        pass
                    try:
                        self.proxies.remove(urlparse(proxies.get('https')).netloc)
                    except:
                        pass
                        
            for pr in self.proxies:
                proxies = self.build_proxy(pr)
                debug(proxies = proxies)
                self.sess.proxies.update(proxies)
                req, error, error_type, error_full = browser(url, rtype, headers, data, params, timeout, retries, sleep, proxies)
                if req:
                    self.config.write_config('proxy', 'http', pr)
                    self.config.write_config('proxy', 'https', pr)
                    index = self.proxies.index(pr) + 1
                    self.proxies = self.proxies[index:]
                    self.use_proxy_config = True
                    self.use_proxy_config_download = True
                    break
        
        debug(req = req)
        debug(error = error)
        #pause()
        if req:
            self.config.write_config('cookies', 'cookies', str(self.sess.cookies.get_dict()))
        if error:
            print(make_colors("ERROR:", 'b', 'y') + " " + make_colors(error_type, 'lw', 'r'))
            if os.getenv('DEBUG'):
                print(make_colors("TRACEBACK:", 'b', 'y') + " " + make_colors(error_full, 'lw', 'bl'))
            return False
        return req
    
    def pause(self, page=''):
        lineno = str(inspect.stack()[1][2])		
        if page:
            page = make_colors("[" + str(page) + "]", "lw", "bl")
        else:
            page = make_colors("[" + str(lineno) + "]", "lw", "bl")
        note = make_colors("Enter to Continue . ", "lw", "lr") + "[" + page + "] " + make_colors("x|q = exit|quit", "lw", "lr")
        print(note)
        q = getch.getch()
        if q == 'x' or q == 'q':
            sys.exit(make_colors("EXIT !", 'lw','lr'))
    
    def login(self, username=None, password=None, url_code = 'login.pl', relogin = False, timeout = None):
        cookies = ''
        error = False
        if self.config.get_config('cookies', 'cookies') and not relogin:
            try:
                cookies = json.loads(self.config.get_config('cookies', 'cookies'))
            except:
                try:
                    cookies = ast.literal_eval(self.config.get_config('cookies', 'cookies'))
                except:
                    pass
        if cookies:
            self.sess.cookies.update(cookies)
            return True
        if not username:
            username = self.config.get_config('auth', 'username')
        if not password:
            password = self.config.get_config('auth', 'password')
        if not username:
            username = raw_input('USERNAME (eMail): ')
            if username:
                self.config.write_config('auth', 'username', username)
        if not password:
            from getpass import getpass
            password = getpass('PASSWORD: ')
            if password:
                self.config.write_config('auth', 'password', password)
        url = self.url + url_code
        data = {
            'mail':username,
            'pass':password,
            'lt':'on',
            'purge':'on',
            'valider':'OK'
        }

        debug(data = data)

        #a = self.sess.post(url, data = data)

        a = self.request(url, data = data, rtype = 'post', timeout = timeout)
        
        debug(a = a)
        #pause()
        if not a:
            return False
        
        # print("CONTENT:")
        # print(a.content)
        content = a.content
        debug(content = content)
        b = bs(content, 'lxml')
        debug(sess_proxy = self.sess.proxies)
        bloc = b.find('div', {'class':'bloc2'})
        debug(bloc =  bloc)

        if bloc and "temporarily locked" in bloc.text:
            print(make_colors(list(set([re.sub(i, make_colors(i, 'b', 'lc'), bloc.text) for i in re.findall("\d+\.\d+\.\d+\.\d+", bloc.text)]))[0], 'lw', 'r'))
            return False
        #     if self.logined:
        #         debug(login = "return False")
        #         return False
        #     else:
        #         if not self.use_proxy:
        #             # print(make_colors(bloc.text, 'lightwhite', 'lightred'))
        #             self.logined = True
        #             self.auto_proxy()
        #             self.use_proxy = True
        #         else:
        #             return False
        # elif not a:
        #     print(make_colors("Login Failed !", 'lw', 'r'))
        #     sys.exit()
        
        #print("content =", content)
        
        cookies_0 = a.cookies
        cookies_1 = self.sess.cookies
        if cookies_1.get_dict():
            self.config.write_config('cookies', 'cookies', str(cookies_1.get_dict()))
        debug(cookies_0 = cookies_0)
        debug(cookies_1 = cookies_1)
        return True
    
    def auto_proxy(self, url = None, no_verify = False, use_all = False, force_https = False, force_http = False, proxy = {}):
        if not url:
            url = self.url
        scheme = urlparse(url).scheme
        n_try = 1
        pc = proxy_tester()
        list_proxy = pc.getProxyList()
        proxies = {}
        #bar = progressbar.ProgressBar(max_value = self.max_value, prefix = self.prefix, variables = self.variables)
        if not proxy:
            while 1:
                self.bar.max_value = len(list_proxy)
                c = ''
                for i in list_proxy:
                    debug(use_proxy = i)
                    proxies = {}
                    proxy_str = ''
                    if no_verify:
                        if use_all:
                            if force_https:
                                proxies.update({'https': 'https://' + str(i.get('ip') + ":" + i.get('port')),})
                                proxy_str = 'https://' + str(i.get('ip') + ":" + i.get('port'))
                            elif force_http:
                                proxies.update({'http': 'http://' + str(i.get('ip') + ":" + i.get('port')),})
                                proxy_str = 'http://' + str(i.get('ip') + ":" + i.get('port'))                                    
                            else:
                                proxies.update({
                                    'https': 'https://' + str(i.get('ip') + ":" + i.get('port')),
                                    'http': 'http://' + str(i.get('ip') + ":" + i.get('port')),
                                                                })
                                proxy_str = str(i.get('ip') + ":" + i.get('port'))
                        else:
                            if i.get('https') == 'yes':
                                if force_http:
                                    proxies.update({'http': 'http://' + str(i.get('ip') + ":" + i.get('port')),})
                                    proxy_str = 'http://' + str(i.get('ip') + ":" + i.get('port'))
                                else:
                                    proxies.update({'https': 'https://' + str(i.get('ip') + ":" + i.get('port')),})
                                    proxy_str = 'https://' + str(i.get('ip') + ":" + i.get('port'))
                            else:
                                if force_https:
                                    proxies.update({'https': 'https://' + str(i.get('ip') + ":" + i.get('port')),})
                                    proxy_str = 'https://' + str(i.get('ip') + ":" + i.get('port'))                                        
                                else:
                                    proxies.update({'http': 'http://' + str(i.get('ip') + ":" + i.get('port')),})
                                    proxy_str = 'http://' + str(i.get('ip') + ":" + i.get('port'))
                        self.bar.update(n_try, task = make_colors("Check Proxy", 'black', 'lightgreen'), subtask = make_colors(i.get('ip') + ":" + i.get('port'), 'lightwhite', 'lightblue') + " ")
                        try:
                            # requests.request('GET', url, proxies=proxies, verify=False, timeout=3)
                            self.request(url, 'GET', proxies=proxies, verify=False, timeout=3)
                            debug(proxies = proxies)
                            #print("\n")
                            #print(make_colors("Use proxy: ", 'lightyellow') + make_colors(proxies.get(scheme), 'lightwhite', 'blue'))
                            self.bar.update(n_try, task = make_colors("Try Proxy", 'lightwhite', 'lightred'), subtask = make_colors(proxy_str, 'lightwhite', 'lightblue') + " ")
                            self.sess.proxies = proxies
                            c = self.login()
                            if c:
                                break

                        except:
                            self.bar.max_value = len(list_proxy)
                            self.bar.value = n_try

                        debug(n_try = n_try)
                        if n_try == len(list_proxy):
                            break
                        else:
                            n_try += 1                            
                    else:
                        if scheme == 'https' and i.get('https') == 'yes':
                            proxies = {scheme: str(scheme + "://" + i.get('ip') + ":" + i.get('port')),}
                            self.bar.update(n_try, task = make_colors("Match Proxy", 'black', 'lightgreen'), subtask = make_colors(proxies.get(scheme), 'lightwhite', 'lightblue') + " ")
                            try:
                                # requests.request('GET', url, proxies=proxies, timeout=3)
                                self.request(url, 'GET', proxies=proxies, timeout=3)
                                #print("\n")
                                #print(make_colors("Use proxy: ", 'lightyellow') + make_colors(proxies.get(scheme), 'lightwhite', 'blue'))
                                self.bar.update(n_try, task = make_colors("Try Proxy", 'lightwhite', 'lightred'), subtask = make_colors(proxies.get(scheme), 'lightwhite', 'lightblue') + " ")
                                debug(proxies = proxies)
                                self.sess.proxies = proxies
                                c = self.login()
                                if c:
                                    break
                            except:
                                self.bar.max_value = len(list_proxy)
                                self.bar.value = n_try
                        else:
                            self.bar.value + 1
                        debug(n_try = n_try)
                        if n_try == len(list_proxy):
                            break
                        else:
                            n_try += 1


                if n_try == len(list_proxy):
                    self.bar.finish()
                    print("\n")
                    print(make_colors("[ERROR] No Proxy is Matched !", 'lightwhite', 'lightred', ['blink']))
                    break                    
                if c:
                    break   
        else:
            debug(proxy = proxy)
            if proxy:
                self.sess.proxies = proxy
                proxies = proxy
            self.bar.max_value = 100
            c = self.login()
            if not c:
                self.bar.update(100, task = make_colors("ERROR", 'lightwhite', 'lightred'), subtask = make_colors("[ERROR CONNECTION]", 'lightred', 'lightyellow') + " ")
                sys.exit(make_colors("[ERROR CONNECTION]", 'lightwhite', 'lightred') + make_colors('Try Again !', 'black', 'lightyellow'))
        return proxies

    def build_proxy(self, proxy):
        proxies = {}
        if not isinstance(proxy, dict) and proxy:
            proxies = {'http':'http://' + proxy, 'https':'https://' + proxy}
        else:
            if proxy:
                if not proxy.get('http') and proxy.get('https'):
                    proxy_parser = urlparse(proxy.get('https'))
                    proxy.update({'http': 'http://' + proxy_parser.netloc})
                elif not proxy.get('https') and proxy.get('http'):
                    proxy_parser = urlparse(proxy.get('http'))
                    proxy.update({'https': 'https://' + proxy_parser.netloc})            
            proxies = proxy
        if not proxies or proxies == {}:
            proxies = {}
        return proxies
    
    def clean_dones(self, proxy = None):
        proxies = {}
        if proxy:
            proxies = self.build_proxy()

        if not self.check_cookies(self.sess.cookies).get('SID'):
            debug("login not use proxies")
            self.login()
        if not self.check_cookies(self.sess.cookies).get('SID'):
            debug("re login not use proxies")
            self.login(relogin = True)
        url = self.url + "console/remote.pl?r=all"
        return self.request(url, proxies = proxies)
    
    def get_download_link_info(self, bs_object = None, url = None):
        if not bs_object:
            if url:
                a = requests.get(url)
                if not a:
                    print(make_colors("Get link info Failed !", 'lw', 'r'))
                    return False
                bs_object = bs(a.content, 'lxml')
            else:
                return False
        b = bs_object
        table = b.find('table', {'class':'premium'})
        debug(table = table)
        info = {}
        if table:
            all_tr = table.find_all('tr')
            if all_tr:
                name = all_tr[0].find_all('td')[2].text
                debug(name = name)
                date = all_tr[1].find_all('td')[1].text
                debug(date = date)
                size = all_tr[2].find_all('td')[1].text
                debug(size = size)
                info.update({
                    'name':name,
                    'date':date,
                    'size':size
                })
        return info

    def get_hidden(self, url, proxy = None, timeout = None):
        timeout = self.timeout or 10
        proxies = self.build_proxy(proxy)
        debug(proxies = proxies)
        a = None
        error = error_full = error_type = None
        sleep = self.sleep
        retries = 3
        if self.download_login:
            if not self.check_cookies(self.sess.cookies).get('SID'):
                debug("login not use proxies")
                self.login()
            if not self.check_cookies(self.sess.cookies).get('SID'):
                debug("re login not use proxies")
                self.login(relogin = True)
        a = self.request(url, proxies = proxies, retries = retries)
        if not a:# or error:
            try:
                print(make_colors("Get download link [1] Failed ! [{}]".format(a.status_code), 'lw', 'r'))
            except:
                pass
            return False, False
        
        with open("get_download_link.html", 'wb') as ff:
            if a.content:
                ff.write(a.content)
            else:
                ff.write('')

        b = bs(a.content, 'lxml')
        hidden = b.find('input', {'type':'hidden'})
        return hidden, b

    def get_download_link(self, url, print_wait = True, retries = 10, proxy = None, timeout = None, retries_proxy = 2, max_try_replay = 2):
        #os.environ.update({"DEBUG": "1",})
        status = False
        max_try_replay = max_try_replay or self.max_try_replay
        b1 = None
        #if self.download_login:
            #self.download_login = False
        timeout = timeout or self.timeout or 10
        retries = retries or self.retries or 10
        debug(url = url)
        warn_minutes = False
        info = {}
        proxies = {}
        error_type = ''
        error_full = ''
        error = False
        sleep = self.sleep or 10
        if proxy:
            proxies = self.build_proxy(proxy)
            debug(proxies = proxies)
        debug(self_download_login = self.download_login)
        hidden, b = self.get_hidden(url, proxies, timeout)
        debug(hidden = hidden)
        
        if os.getenv('DEBUG') == '1':
            pause()
        if hidden:
            if proxies:
                if proxies.get('http'):
                    try:
                        self.config.write_config('download_proxy', 'http', urlparse(proxies.get('http')).netloc)
                    except:
                        pass
                if proxies.get('https'):
                    try:
                        self.config.write_config('download_proxy', 'https', urlparse(proxies.get('https')).netloc)
                    except:
                        pass
        else:
            self.download_login = False
            return self.get_download_link(url, print_wait, retries, proxy, timeout, retries_proxy, max_try_replay)
        if os.getenv('DEBUG') == '1':
            pause()    
        bloc2 = b.find('div', {'class':'bloc2'})
        debug(bloc2 = bloc2)
        debug(self_download_login = self.download_login)
        if os.getenv('DEBUG') == '1':
            pause()
        if bloc2:
            debug(bloc2_text = bloc2.text)
            debug(str_bloc2 = str(bloc2))
            bloc3 = re.sub("<br/>", " - ", str(bloc2))
            debug(bloc3 = bloc3)
            b1 = bs(bloc3, 'lxml')
            error_text = b1.find('div')
            if error_text:
                error_text = re.sub("\\n", "", error_text.text)
            else:
                error_text = ''

            debug(error_text = error_text)
            if "does not exist" in error_text or "deleted" in error_text:
                print(make_colors(error_text.strip(), 'lw', 'r'))
                return False, warn_minutes, info
        debug(hidden = hidden)
        data = {'adz':hidden.get('value')}
        debug(data = data)
        debug(self_download_login = self.download_login)
        if os.getenv('DEBUG') == '1':
            pause()
        a1 = None
        #if login or self.download_login:
            #a1 = self.requests(url, 'post', data=data, proxies = proxies)
        #else:
        nt = 1
        mt = 1
        while 1:
            try:
                debug(proxies = proxies)
                a1 = self.requests(url, data=data, proxies = proxies, timeout = timeout, rtype = 'post')
                break
            except:
                tr, vl, tb = sys.exc_info()
                error_type = vl.__class__.__name__
                if error_type == 'ProxyError':
                    nt = retries
                
                debug(error_type = error_type)
                error_full = traceback.format_exc()
                debug(error_full = error_full)
                debug(nt = nt)
                debug(retries = retries)
                debug(timeout = timeout)
                if not nt == retries or nt < retries:
                    debug("not nt == retries or nt < retries")
                    nt += 1
                    time.sleep(sleep)
                elif nt > retries:
                    debug("not nt == retries or nt < retries")
                    nt == retries
                    if not mt == max_try_replay:
                        mt += 1
                        if timeout < 60:
                            timeout = 60                            
                    else:
                        error = True
                        break                        
                elif nt == retries:
                    debug("nt == retries")
                    if not mt == max_try_replay:
                        mt += 1
                        if timeout < 60:
                            timeout = 60                            
                    else:
                        error = True
                        break
                debug(error = error)
                
        debug(self_download_login = self.download_login)
        if os.getenv('DEBUG') == '1':
            pause()
        if error:
            print(make_colors("Failed to get download link ! with login status is {}".format(str(login)), 'lw', 'r'))
            return False, warn_minutes, info
        if not a1:
            print(make_colors("Get download link [2] Failed !", 'lw', 'r'))
            return False, warn_minutes, info
        else:
            #self.download_login = True
            self.hidden_use_proxy_config = False
            self.hidden_use_proxy_download_config = False
        content = a1.content
        with open("get_download_link.html", 'wb') as ff:
            ff.write(content)
        # debug(content = content)
        b1 = bs(content, 'lxml')
        #debug(b1 = b1)
        link = b1.find('a', {'class':'ok btn-general btn-orange'})#, text=re.compile('Click here to download the file'))
        warn = b1.find_all('div', {'class':"ct_warn"})
        debug(warn = warn)
        debug(link = link)
        debug(self_download_login = self.download_login)
        if os.getenv('DEBUG') == '1':
            pause()
        if link:
            info = self.get_download_link_info(b, url)
            if not info:
                info = self.get_download_link_info(b1, url)
            debug(download_link = link.get('href'))
            debug(info = info)
            self.download_login = True
            return True, link.get('href'), info
        elif not link and self.download_login:
            self.download_login = False
            return self.get_download_link(url, print_wait, retries, proxy, timeout, retries_proxy, max_try_replay)
        else:
            debug(proxy = proxy)
            if os.getenv('DEBUG') == '1':
                pause()
            if proxy:
                proxies = self.build_proxy(proxy)
                if not self.proxies:
                    pt = proxy_tester()
                    list_proxy = pt.getProxyList()
                    self.proxies = [i.get('ip') + ":" + i.get('port') for i in list_proxy]                
                if urlparse(proxies.get('http')).netloc in self.proxies:
                    return False, "", info
            if warn:
                if len(warn) > 1:
                    warning = warn[1].text
                else:
                    warning = warn[0].text
                if warning:
                    warning = str(warning).strip()
                debug(warning = warning)
                if warning:
                    warn_minutes = re.findall('wait(.*?)minutes', warning)
                    debug(warn_minutes = warn_minutes)
                    if warn_minutes:
                        warn_minutes = warn_minutes[0].strip()
                        debug(warn_minutes = warn_minutes)
                    else:
                        debug(warn_minutes = warn_minutes, debug = True)
                        if os.getenv('DEBUG') == '1':#
                            pause()
                    warning = re.sub("  ", " ", warning)
                    warning = re.sub("  ", " ", warning)
                    warning = re.sub("  ", " ", warning)
                    warning = re.sub("\n", " ", warning)
                    warning = re.sub("\r", "", warning)
                    if print_wait:
                        print(make_colors(warning, 'lightwhite', 'lightred', ['blink']))
                    debug(warn_minutes = warn_minutes)
                    if (str(warn_minutes).isdigit() and int(warn_minutes) > 1) or not warn_minutes:
                        debug("(str(warn_minutes).isdigit() and int(warn_minutes) > 1) or not warn_minutes")
                        if os.getenv('DEBUG') == '1':
                            pause()
                        status = False
                        if not self.use_proxy_config:
                            if os.getenv('DEBUG') == '1':
                                pause()
                            proxies = {}
                            if self.config.get_config('proxy', 'http') or self.config.get_config('proxy', 'https'):
                                if os.getenv('DEBUG') == '1':
                                    pause()
                                if self.config.get_config('proxy', 'http'):
                                    proxies.update({'http':'http://' + self.config.get_config('proxy', 'http')})
                                    proxies.update({'https':'https://' + self.config.get_config('proxy', 'http')})
                                if self.config.get_config('proxy', 'https'):
                                    proxies.update({'https':'https://' + self.config.get_config('proxy', 'https')})
                                
                                debug(proxies = proxies)
                                status, link, info = self.get_download_link(url, False, proxy = proxies)
                                debug(status = status)
                                debug(link = link)
                                debug(info = info)
                                if os.getenv('DEBUG') == '1':
                                    pause()
                            debug(status = status)
                            if os.getenv('DEBUG') == '1':
                                pause()
                            if status:
                                if os.getenv('DEBUG') == '1':
                                    pause()
                                try:
                                    self.config.write_config('download_proxy', 'http', urlparse(proxies.get('http')).netloc)
                                except:
                                    pass
                                try:
                                    self.config.write_config('download_proxy', 'https', urlparse(proxies.get('https')).netloc)
                                except:
                                    pass
                                self.use_proxy_config = False
                                self.download_login = True
                                return status, link, info
                            self.use_proxy_config = True
                            if os.getenv('DEBUG') == '1':
                                pause()
                        debug(status = status)
                        debug(self_use_proxy_config_download = self.use_proxy_config_download)
                        if os.getenv('DEBUG') == '1':
                            pause()
                        if not self.use_proxy_config_download and not status:
                            if os.getenv('DEBUG') == '1':
                                pause()
                            proxies = {}
                            if self.config.get_config('proxy', 'http') or self.config.get_config('download_proxy', 'https'):
                                if self.config.get_config('download_proxy', 'http'):
                                    proxies.update({'http':'http://' + self.config.get_config('download_proxy', 'http')})
                                    proxies.update({'https':'https://' + self.config.get_config('download_proxy', 'http')})
                                if self.config.get_config('download_proxy', 'https'):
                                    proxies.update({'https':'https://' + self.config.get_config('download_proxy', 'https')})
                                self.use_proxy_config_download = True
                                status, link, info = self.get_download_link(url, False, proxy = proxies)
                            debug(status = status)
                            if os.getenv('DEBUG') == '1':
                                pause()
                            if status:
                                self.download_login = True
                                return status, link, info
                            self.use_proxy_config_download = True
                        if not status:
                            if os.getenv('DEBUG') == '1':
                                pause()
                            ntp = 0
                            while 1:
                                if not self.proxies:
                                    pt = proxy_tester()
                                    list_proxy = pt.getProxyList()
                                    self.proxies = [i.get('ip') + ":" + i.get('port') for i in list_proxy]                                    
                                if not ntp == retries_proxy or ntp < retries_proxy:
                                    ntp += 1
                                elif ntp > retries or ntp == retries:
                                    ntp == retries                                    
                                    if print_wait:
                                        print(make_colors("waiting for: 2 seconds for {} minutes".format(warn_minutes), 'lightwhite', 'lightred', ['blink']))
                                    sys.stdout.write(".")
                                    sys.stdout.flush()
                                    time.sleep(2)
                                    #self.use_proxy_proxies = True
                                    #return self.get_download_link(url, False)
                                    break
                                else:
                                    for pr in self.proxies:
                                        proxies = self.build_proxy(pr)
                                        self.sess.proxies.update(proxies)
                                        status, link, info = self.get_download_link(url, False, proxy = proxies) 
                                        if status:
                                            self.config.write_config('download_proxy', 'http', pr)
                                            self.config.write_config('download_proxy', 'https', pr)
                                            self.config.write_config('proxy', 'http', pr)
                                            self.config.write_config('proxy', 'https', pr)
                                            self.use_proxy_config = False
                                            self.use_proxy_config_download = False
                                            self.download_login = True
                                            try:
                                                index = self.proxies.index(pr) + 1
                                                self.proxies = self.proxies[index:]
                                            except:
                                                pass
                                            return status, link, info
                        if os.getenv('DEBUG') == '1':
                            pause()
                    elif str(warn_minutes).isdigit() and int(warn_minutes) == 1:
                        debug("str(warn_minutes).isdigit() and int(warn_minutes) == 1")
                        if os.getenv('DEBUG') == '1':
                            pause()
                        time.sleep(10)
                        if print_wait:
                            print(make_colors("waiting for: 1 minute", 'lightwhite', 'lightred', ['blink']))
                        return self.get_download_link(url) 
                    elif str(warn_minutes).isdigit() and int(warn_minutes) <= 1:
                        debug("str(warn_minutes).isdigit() and int(warn_minutes) <= 1")
                        if os.getenv('DEBUG') == '1':
                            pause()
                        time.sleep(2)
                        if print_wait:
                            print(make_colors("waiting for: 2 seconds for {} minutes".format(warn_minutes), 'lightwhite', 'lightred', ['blink']))
                        sys.stdout.write(".")
                        sys.stdout.flush()
                        return self.get_download_link(url, False) 
                    else:
                        debug("else")
                        if os.getenv('DEBUG') == '1':
                            pause()
                        if warn_minutes:
                            time.sleep(int(warn_minutes) / 2)
                        else:
                            time.sleep(1)
                        if print_wait:
                            print(make_colors("waiting for: {} minute for {}".format(int(warn_minutes) / 2, warn_minutes), 'lightwhite', 'lightred', ['blink']))
                        return self.get_download_link(url) 
                return False, warn_minutes, info
        #os.environ.update({"DEBUG": "0",})
        return False, warn_minutes, info

    def get_sable(self, timeout = None):
        url = self.url + 'console/files.pl?dir_id=0&oby=0&search='
        sable = ''
        def get(proxies = {}):
            sable = ''
            a = self.request(url, timeout = timeout)
            debug(a = a)
            #pause()
            if a:
                debug(url = a.url)
                content = a.content
                with open('list.html', 'wb') as ff:
                    ff.write(content)
                debug(content = content)
                debug(sess_cookies = self.sess.cookies)
                try:
                    debug(SID = self.sess.cookies.get('SID'))
                except:
                    debug(SID = self.sess.cookies.get_dict().get('SID'))
                b = bs(content, 'lxml')
                try:
                    sable = b.find('ul', {'id':'sable'}).find_all('li')
                    return sable
                except:
                    sable = ''
                debug(sable = sable)
            return sable
        
        sable = get()
        debug(sable = sable)
        #pause()
        
        if not sable and (self.config.get_config('proxy', 'http') or self.config.get_config('proxy', 'https')):
            proxies_conf = {}
            print(make_colors("Use Proxy from config", 'lw', 'r'))
            if self.config.get_config('proxy', 'http'):
                proxies_conf = {'http':'http://' + self.config.get_config('proxy', 'http')}
            elif self.config.get_config('proxy', 'http'):
                proxies_conf = {'https':'https://' + self.config.get_config('proxy', 'http')}
            sable = get(proxies_conf)
            if not sable:
                self.config.write_config('proxy', 'http', '')
                self.config.write_config('proxy', 'https', '')
            else:
                self.config.write_config('cookies', 'cookies', srt(self.sess.cookies.get_dict()))

        if not sable and (self.config.get_config('download_proxy', 'http') or self.config.get_config('download_proxy', 'https')):
            proxies_conf = {}
            print(make_colors("Use Proxy from config download", 'lw', 'r'))
            if self.config.get_config('download_proxy', 'http'):
                proxies_conf = {'http':'http://' + self.config.get_config('download_proxy', 'http')}
            elif self.config.get_config('download_proxy', 'http'):
                proxies_conf = {'https':'https://' + self.config.get_config('download_proxy', 'http')}
            sable = get(proxies_conf)
            if not sable:
                self.config.write_config('download_proxy', 'http', '')
                self.config.write_config('download_proxy', 'https', '')
            else:
                self.config.write_config('cookies', 'cookies', srt(self.sess.cookies.get_dict()))

        if not sable:
            print(make_colors("Use Proxy from self.proxies", 'lw', 'r'))
            if not self.proxies:
                pt = proxy_tester()
                list_proxy = pt.getProxyList()
                self.proxies = [i.get('ip') + ":" + i.get('port') for i in list_proxy]
            for pr in self.proxies:
                proxies = self.build_proxy(pr)
                debug(proxies = proxies)
                self.sess.proxies.update(proxies)
                sable = get(proxies)
                if sable:
                    self.config.write_config('proxy', 'http', pr)
                    self.config.write_config('proxy', 'https', pr)
                    index = self.proxies.index(pr) + 1
                    self.proxies = self.proxies[index:]
                    self.config.write_config('cookies', 'cookies', srt(self.sess.cookies.get_dict()))
            if not sable:
                self.proxies = []
                    
        return sable

    def get_next_proxy(self, list_proxy, referer_proxy):
        index = None
        proxies = {}
        try:
            index = list_proxy.index(urlparse(referer_proxy.get('http')).netloc)
        except:
            pass
        if not index:
            try:
                index = list_proxy.index(urlparse(referer_proxy.get('https')).netloc)
            except:
                pass
        debug(index = index)
        if index:
            if not index > len(list_proxy):
                proxies = {'http': 'http://' + list_proxy[index + 1], 'https': 'https://' + list_proxy[index + 1]}
            debug(proxies = proxies)
            try:
                list_proxy.remove(list_proxy[index + 1])
            except:
                pass
        else:
            if isinstance(list_proxy, list):
                proxies = {'http': 'http://' + list_proxy[0], 'https': 'https://' + list_proxy[0]}

        return proxies, list_proxy
    
    def list(self, retries = 5, timeout = 60):

        data = []
        url = self.url + 'console/files.pl?dir_id=0&oby=0&search='
        debug(url = url)

        debug(self_session_cookies = self.sess.cookies)
        debug(check_cookies = self.check_cookies(self.sess.cookies))
        #pause()
        if not self.check_cookies(self.sess.cookies).get('SID'):
            debug("login not use proxies")
            self.login()
        if not self.check_cookies(self.sess.cookies).get('SID'):
            debug("re login not use proxies")
            self.login(relogin = True)
        
        #pause()
        n = 1
        error = False

        sable = self.get_sable(timeout)
        debug(sable = sable)
        debug(SID = self.sess.cookies)
        debug(SID = self.sess.cookies.get_dict())
        try:
            debug(SID = self.sess.cookies.get('SID'))
        except:
            pass
        debug(sable = sable)
        #pause()
        if not sable:
            print(make_colors("ERROR:", 'lw', 'r') + " " + make_colors("error get data !", 'r', 'lw'))
            return False, 0
        #pause()
        sizes = []
        total = 0
        if sable:
            for i in sable:
                rel = i.get('rel')
                debug(rel = rel)
                name = i.find('a').text
                debug(name = name)
                date = i.find('div', {'class':'dD'}).text
                debug(date = date)
                size = i.find('div', {'class':'dS'}).text
                sizes.append(size)
                debug(size = size)
                data_add = {'rel':rel, 'name':name, 'size':size, 'date': date, 'timestamp':self.format_date(date, format_date = '%Y-%m-%d %H:%M')[1]}
                data.append(data_add)
            debug(data = data)
            #self.build_dict(data, key = 'timestamp')

            for i in sizes:
                size, stype = re.split(' ', i)
                debug(size = size)
                debug(stype = stype)
                data_size = Size.convert(str(size).strip(), str(stype).strip())
                debug(data_size = data_size)
                total += data_size
            total = Size.total(total)
            debug(total = total)
            return data, total
        else:
            print(make_colors("No DATA !", "lightwhite", "lightred", ['blink']))
            return False, 0

    def refresh(self, sort_by = 'time'):
        check_sort_by = ['rel', 'name', 'date', 'size', 'timestamp/time']
        data, total = self.list()
        debug(data = data)
        debug(sort_by = sort_by)
        if str(sort_by).lower().strip() == 'time':
            sort_by = 'timestamp'
        debug(sort_by_check = re.findall(sort_by, " ".join(check_sort_by), re.I))
        if sort_by and re.findall(sort_by, " ".join(check_sort_by), re.I):
            debug(sort_by = sort_by)
            data = sorted(data, key=lambda y: y.get(sort_by))
            debug(data = data)
        self.data = data
        self.total = total
        # #pause()
        return data, total
    
    def download(self, url, download_path=os.getcwd(), confirm=False, use_wget=False, name = None):
        if use_wget:
            wget.download(url, download_path)
        else:
            if not sys.platform == 'win32':
                import downloader
                downloader.download_linux(url, self.config, download_path=download_path, saveas=name, downloader = 'wget')
            else:
                try:
                    idm = IDMan()
                    idm.download(url, download_path, name, confirm=confirm)
                except:
                    traceback.format_exc()
                    if name:
                        download_path = os.path.join(download_path, name)
                    wget.download(url, download_path)

    def check_cookies(self, cookies):
        debug(cookies = cookies)
        if not cookies:
            return {}
        cookies = str(cookies)
        debug(cookies = cookies)
        data = re.findall('SID=(.*?) ', cookies)
        debug(data = data)
        if data and data[0]:
            data = filter(None, data)[0]
            debug(data = data)
            return {'SID':data}
        return {}
        

    def navigator(self, username = None, password = None, no_verify = False, use_all = False, force_https = False, force_http = False, proxy = {}, minute_add = None, download_path = os.getcwd(), confirm = False, force_wget = False, q = None, data = None, print_list = True, sort_by = 'date', direct_download_number = None):
        check_sort_by = ['rel', 'name', 'date', 'size', 'timestamp']
        total = self.total or 0
        debug(self_session_cookies = self.sess.cookies)
        debug(self_session_cookies = self.sess.cookies.get_dict())
        if not self.check_cookies(self.sess.cookies).get('SID'):
            self.login(username, password)
        if not self.check_cookies(self.sess.cookies).get('SID'):
            debug("login not use proxies")
            self.login()
        if not self.check_cookies(self.sess.cookies).get('SID'):
            debug("re login not use proxies")
            self.login(relogin = True)
        debug(sort_by = sort_by)
        debug(data = data)
        if self.data:
            data = self.data
        debug(data = data)
        debug(self_session_cookies = self.sess.cookies)
        debug(self_session_cookies_str = str(self.sess.cookies))
        debug(check_cookies = self.check_cookies(self.sess.cookies))
        try:
            debug(self_session_cookies = self.sess.cookies.get_dict())
        except:
            pass
        
        #pause()
        if not data:
            data, total = self.list()
            self.data = data
            debug(data = data)
            
        else:
            self.data = data
            debug("data is it")
        debug(sort_by = sort_by)
        # if sort_by:
        #     debug(sort_by = sort_by)
        #     data, total = self.list()
            
        if str(sort_by).lower().strip() == 'time':
            sort_by = 'timestamp'
        debug(sort_by_check = re.findall(sort_by, " ".join(check_sort_by), re.I))
        if sort_by and len(re.findall(sort_by, " ".join(check_sort_by), re.I)) == 1:
            debug(sort_by = sort_by)
            if sort_by == 'size':
                data = sorted(data, key=lambda y: bitmath.parse_string_unsafe(y.get(sort_by)).kB.value)
            else:
                data = sorted(data, key=lambda y: y.get(sort_by))
        
        
        debug(data = data)			
        debug(print_list = print_list)
        #pause()
        if print_list and data:
            n = 1
            for i in data:
                if len(str(n)) == 1:
                    number = "0" + str(n)
                else:
                    number = str(n)
                #     print(make_colors(number, 'lightcyan') + ". " + make_colors(data.get(i).get('name'), 'lightwhite', 'lightblue') + " [" + make_colors(data.get(i).get('size'), 'black', 'lightgreen') + "] [" + make_colors(data.get(i).get('date'), 'lightwhite', 'magenta') + "]")
                # else:
                print(make_colors(number, 'lightcyan') + ". " + make_colors(i.get('name'), 'lightwhite', 'lightblue') + " [" + make_colors(i.get('size'), 'black', 'lightgreen') + "] [" + make_colors(i.get('date'), 'lightwhite', 'magenta') + "]")
                n += 1
            total = total or self.total
            print(make_colors("TOTAL Size:", 'lw', 'b') + " " + make_colors(str(total) , 'b', 'lg'))
        debug(direct_download_number = direct_download_number)
        if isinstance(direct_download_number, list):
            for d in direct_download_number:
                if str(d).strip().isdigit():
                    debug(d = d)
                    self.navigator(username, password, no_verify, use_all, force_https, force_http, proxy, minute_add, download_path, confirm, force_wget, str(d) + "d", data, False, sort_by)
        else:
            if str(direct_download_number).strip().isdigit():
                self.navigator(username, password, no_verify, use_all, force_https, force_http, proxy, minute_add, download_path, confirm, force_wget, str(direct_download_number).strip() + "d", data, False, sort_by)
        debug(q = q)
        if not q:
            q = self.print_nav()
        #bar = progressbar.ProgressBar(max_value = self.max_value, prefix = self.prefix, variables = self.variables)
        
        if q:
            q = str(q).strip()
            if q and str(q).isdigit() and int(q) <= len(data):
                debug("q is digit")
                task = make_colors("Download Link", 'lightwhite', 'blue')
                subtask = make_colors("Get", 'lightwhite', 'magenta') + " "
                self.bar.update(self.bar.value + 1, task = task, subtask = subtask)
                
                debug(data_selected = data[int(q) - 1])
                link = self.download_link(data[int(q) - 1].get('rel'))
                name = unidecode(data[int(q) - 1].get('name'))

                task = make_colors("Generator", 'lightwhite', 'blue')
                subtask = make_colors("Convert", 'lightwhite', 'magenta') + " "
                self.bar.update(self.bar.value + 1, task = task, subtask = subtask)
                download_link = self.get_download_link(link)
                if download_link[0]:
                    print(make_colors("GENERATE:", 'r', 'lw') + " " + make_colors(download_link[1], 'b', 'ly'))
                    print(make_colors("NAME    :", 'lw', 'bl') + " " + make_colors(download_link[2].get('name'), 'lw', 'bl'))
                    print(make_colors("SIZE    :", 'b', 'lg') + " " + make_colors(download_link[2].get('size'), 'b', 'lg'))
                    print(make_colors("DATE    :", 'lw', 'm') + " " + make_colors(download_link[2].get('date'), 'lw', 'm'))
                    qp = raw_input(make_colors("Enter to Continue [enter]", 'b', 'lg'))
                else:
                    print(make_colors("GENERATE:", 'r', 'lw') + " " + make_colors("FAILED !", 'lw', 'r'))
            elif q and q[-1:] == 'd':# and q[:-1].isdigit():
                all_number_selected = []
                if len(str(q).strip()) > 1:
                    number_selected = str(q).strip()[:-1]
                else:
                    number_selected = raw_input(make_colors("Select number to download: ", 'lightwhite', 'lightred'))
                debug(number_selected = number_selected, debug = True)
                if "," in number_selected or " " in number_selected:
                    debug("method 1", debug = True)
                    number_selected = re.sub(" ", "", number_selected)
                    number_selected = re.split(",| ", number_selected)
                    all_number_selected += number_selected
                    number_selected = list(set(all_number_selected))
                elif "-" in number_selected:
                    debug("method 2", debug = True)
                    number_selected = re.sub(" ", "", number_selected)
                    debug(number_selected = number_selected)
                    number_selected = re.split("-", number_selected)
                    debug(number_selected = number_selected)
                    number_selected = list(range(int(number_selected[0]), (int(number_selected[1]) + 1)))
                    debug(number_selected = number_selected)
                    all_number_selected += number_selected
                    number_selected = list(set(all_number_selected))
                else:
                    number_selected = [number_selected]
                    
                debug(number_selected = number_selected, debug = True)
                # #pause()

                debug("q containt 'd'")
                debug(number_selected = sorted(number_selected), debug = True)
                for qn in sorted(number_selected):
                    task = make_colors("Download Link", 'lightwhite', 'blue')
                    subtask = make_colors("Get", 'lightwhite', 'magenta') + " "
                    self.bar.update(self.bar.value + 1, task = task, subtask = subtask)
                    #print("data.get(list(data.keys())[0]).keys() =", data.get(list(data.keys())[0]).keys())
                    debug(data_selected = data[int(qn) - 1])
                    link = self.download_link(data[int(qn) - 1].get('rel'))
                    name = unidecode(data[int(qn) - 1].get('name'))

                    task = make_colors("Download Link", 'lightwhite', 'blue')
                    subtask = make_colors("Convert", 'lightwhite', 'magenta') + " "
                    self.bar.update(self.bar.value + 1, task = task, subtask = subtask)
                    download_link = self.get_download_link(link)
                    debug(download_link = download_link)
                    task = make_colors("Download", 'lightwhite', 'blue')
                    subtask = make_colors(name, 'lightred', 'lightyellow') + " "
                    self.bar.update(self.bar.value + 1, task = task, subtask = subtask)
                    print(make_colors("DOWNLOAD LINK:", 'b', 'y') + " " + make_colors(download_link[1], 'b', 'c'))
                    print(make_colors("DOWNLOAD PATH:", 'b', 'lc') + " " + make_colors(download_path, 'b', 'c'))
                    if download_link[0]:
                        self.download(download_link[1], download_path, confirm, force_wget, name)
                    else:
                        task = make_colors("Download", 'lightwhite', 'lightred')
                        subtask = make_colors("ERROR Wait for " + download_link[1] + " minutes", 'lightred', 'lightwhite') + " "
                    self.bar.update(self.bar.max_value, task = task, subtask = subtask)					
                    self.bar.value = 0
                    #time.sleep(62)
            elif q and q[-1:] == 'm':
                debug("q containt 'm'")
                if len(str(q).strip()) > 1:
                    number_selected = str(q).strip()[:-1]
                else:
                    number_selected = raw_input(make_colors("Select number to remove: ", 'lightwhite', 'lightred'))
                
                debug(number_selected = number_selected)
                if number_selected and str(number_selected).isdigit() and int(number_selected) <= len(data):
                    self._remove(number_selected, data, sort_by, self.bar)

                elif "," in number_selected or " " in number_selected:
                    #number_selected = re.sub(" ", "", number_selected)
                    list_number_selected = sorted(list(filter(None, re.split(",| ", number_selected))))
                    debug(list_number_selected = list_number_selected)
                    for i in list_number_selected:
                        if i.isdigit():
                            self.bar.max_value = len(list_number_selected)
                            number_selected = str(i).strip()
                            if number_selected and str(number_selected).isdigit() and int(number_selected) <= len(data):
                                self._remove(number_selected, data, sort_by, self.bar)
                            else:
                                task = make_colors("Deleting", "lightwhite", "lightred")
                                subtask = make_colors("ERROR", 'lightwhite', 'lightred') + " "
                                self.bar.update(self.bar.value + 1, task = task, subtask = subtask)

                elif "-" in number_selected:
                    number_selected = re.sub(" ", "", number_selected)
                    debug(number_selected = number_selected)
                    number_selected = re.split("-", number_selected)
                    debug(list_number_selected = list_number_selected)
                    list_number_selected = sorted(list(range(int(number_selected[0]), (int(number_selected[1]) + 1))))
                    debug(list_number_selected = list_number_selected)
                    # list_number_selected_str = str(list_number_selected)[1:-1] + "m"
                    # debug(list_number_selected_str = list_number_selected_str)
                    for i in list_number_selected:
                        self.bar.max_value = len(list_number_selected)
                        number_selected = str(i).strip()
                        if i.isdigit():
                            if number_selected and str(number_selected).isdigit() and int(number_selected) <= len(data):
                                self._remove(number_selected, data, sort_by, self.bar)
                            else:
                                task = make_colors("Deleting", "lightwhite", "lightred")
                                subtask = make_colors("ERROR", 'lightwhite', 'lightred') + " "
                                self.bar.update(self.bar.value + 1, task = task, subtask = subtask)
            elif "rn" in q or "rn=" in q or "rn =" in q:
                debug("q containt 'rn'")
                number_selected = ''
                new_name = ''
                data_rename = re.split("rn=|rn =|rn = |rn= ", q)
                data_rename = filter(None, data_rename)
                debug(data_rename = data_rename)
                if len(data_rename) == 2:
                    number_selected = data_rename[0]
                    debug(number_selected = number_selected)
                    new_name = data_rename[1]
                    if number_selected.isdigit():
                        number_selected = int(number_selected)
                    else:
                        number_selected = raw_input(make_colors("Select number rename to {}:".format(new_name), 'lw', 'r') + " ")
                        if number_selected:
                            if number_selected.isdigit():
                                number_selected = int(number_selected)

                elif len(data_rename) == 1:
                    number_selected = data_rename[0]
                    if number_selected.isdigit():
                        number_selected = int(number_selected)
                    else:
                        new_name = raw_input(make_colors("new name to:", 'lw', 'r') + " ")
                        number_selected = raw_input(make_colors("Select number rename to {}:".format(new_name), 'lw', 'r') + " ")
                        if number_selected:
                            if number_selected.isdigit():
                                number_selected = int(number_selected)

                if number_selected and new_name:
                    if number_selected and int(number_selected) <= len(data):
                        rel = data[int(number_selected) - 1].get('rel')
                        name = data[int(number_selected) - 1].get('name')
                        task = make_colors(name, 'b', 'lg') + " " + make_colors("Rename to", "lightwhite", "lightred")                        
                        subtask = make_colors(new_name, 'lightwhite', 'blue') + " "    
                        self.bar.update(self.bar.max_value/2, task = task, subtask = subtask)
                        #raw_input("Enter to Continue")
                        debug(rel = rel)
                        status, info = self.rename(rel, new_name)
                        if status:
                            subtask = make_colors(new_name, 'lightwhite', 'blue') + " " + make_colors("[SUCCESS]", 'b', 'lg') + " "    
                        else:
                            subtask = make_colors(new_name, 'lightwhite', 'blue') + " " + make_colors("[ERROR:FAILED] [{}]".format(info), 'lw', 'r') + " "    
                        self.bar.update(self.bar.max_value, task = task, subtask = subtask)
            elif q and q[-1:] == 'e' and q[:-1].isdigit():
                debug("q containt 'e'")
                if len(str(q).strip()) > 1:
                    number_selected = str(q).strip()[:-1]
                else:
                    number_selected = raw_input(make_colors("Select number to export: ", 'lightwhite', 'lightred'))
                task = make_colors("Export", "lightwhite", "blue")
                subtask = make_colors("start", 'black', 'lightgreen') + " "
                self.bar.update(self.bar.value + 5, task = task, subtask = subtask)
                if number_selected and str(number_selected).isdigit() and int(number_selected) <= len(data):
                    debug(data_selected = data[int(number_selected) - 1])
                    rel = data[int(number_selected) - 1].get('rel')
                    subtask = make_colors(data[int(number_selected) - 1].get('name'), 'lightwhite', 'blue') + " "
                else:
                    task = make_colors("Export", "lightwhite", "lightred")
                    subtask = make_colors("ERROR", 'lightwhite', 'lightred') + " "
                    self.bar.update(self.bar.max_value, task = task, subtask = subtask)

                task = make_colors("Export", "lightwhite", "blue")
                debug(rel = rel)
                self.export(rel, download_path)
                self.bar.update(self.bar.max_value, task = task, subtask = subtask)
            elif q == 'r':
                debug("q is 'r'")
                qr = raw_input(make_colors("Input Remote URL: ", 'lightwhite', 'blue'))
                if qr:
                    if qr.strip() == 'c':
                        qr = [clipboard.paste()]
                    else:
                        qr = [qr.strip()]
                    if 'http' in qr[0] or 'ftp' in qr[0]:
                        self.remote_upload(qr)
            elif q == "s" in q or "s=" in q or "s =" in q:
                debug("q is 's'")
                sort_by = re.split("s=|s =|s = |s= ", q)
                sort_by = filter(None, sort_by)
                debug(sort_by = sort_by)
                
                if sort_by:
                    sort_by = sort_by[0].strip()
                if not sort_by:
                    sort_by = raw_input(make_colors("Sortby ['rel', 'name', 'date', 'size', 'timestamp']:", 'lw', 'r') + " ")
                    sort_by = sort_by.strip()
                debug(sort_by = sort_by)
                
                return self.navigator(username, password, no_verify, use_all, force_https, force_http, proxy, minute_add, download_path, confirm, force_wget, sort_by = sort_by)
            elif q == 'x' or q == 'q':
                debug("q containt 'x' or 'q'")
                task = make_colors("EXIT", 'lightwhite', 'lightred')
                subtask = make_colors("System Exit !", 'lightwhite', 'lightred') + " "
                self.bar.update(self.max_value, task = task, subtask = subtask)
                print("\n")
                sys.exit(make_colors("EXIT !", 'lightwhite', 'lightred'))
                #sys.exit()
            elif q == 'h' or q == '-h':
                debug("q containt 'h' or '-h")
                print(make_colors("command line option help", 'lw', 'r'))
                help_str = """\t    usage: 1fichier.py [-h] [-s SORT_BY] [-r REMOTE_UPLOAD] [-p DOWNLOAD_PATH]
                        [-d DOWNLOAD] [-w] [-c] [-U USERNAME] [-P PASSWORD]
                        [-x [PROXY [PROXY ...]]] [-nv] [-a] [-http] [-https]

                    optional arguments:
                      -h, --help            show this help message and exit
                      -s SORT_BY, --sort-by SORT_BY
                                            Sortby: time/timestamp, date, name, rel, size
                      -r REMOTE_UPLOAD, --remote-upload REMOTE_UPLOAD
                                            Remote Upload
                      -p DOWNLOAD_PATH, --download-path DOWNLOAD_PATH
                                            Download Path or Export save path
                      -d DOWNLOAD, --download DOWNLOAD
                                            Convert Link and download it
                      -w, --wget            Force use wget as downloader
                      -c, --confirm         Confirm before download it (IDM Only)
                      -U USERNAME, --username USERNAME
                                            Username (email) login
                      -P PASSWORD, --password PASSWORD
                                            Password login
                      -x [PROXY [PROXY ...]], --proxy [PROXY [PROXY ...]]
                                            Via Proxy, example: https://192.168.0.1:3128 https://192.168.0.1:3128 ftp://127.0.0.1:33 or {'http':'127.0.0.1:8080', 'https': '10.5.6.7:5656'} or type 'auto' for auto proxy
                      -nv, --no-verify      Use all type of proxy (http or https)
                      -a, --all             Use all type of proxy (http or https) to session
                      -http, --http         Use all type of proxy (http or https) to session and set to http
                      -https, --https       Use all type of proxy (http or https) to session and set to https"""

                print(make_colors(help_str, 'lightcyan'))

        #raw_input("Enter to Continue")
        print("\n")
        self.data, self.total = self.refresh(sort_by)
        # return self.navigator(username, password, no_verify, use_all, force_https, force_http, proxy, minute_add, download_path, confirm, force_wget, q, data, print_list, sort_by, direct_download_number)
        return self.navigator(username, password, no_verify, use_all, force_https, force_http, proxy, minute_add, download_path, confirm, force_wget, sort_by = sort_by)
    
    def print_nav(self):
        note1 = make_colors(
        "Select Number", 'lightwhite', 'lightblue') + " [" +\
        make_colors("[n] = generate download link", 'b', 'lc') + ", " +\
        make_colors("[n]d = download it", 'b', 'ly') + ", " +\
        make_colors("[n]m = remove n", 'lightwhite', 'lightred') + ", " +\
        make_colors("[n]rn = rename n", 'lightwhite', 'blue') + ", " +\
        make_colors("r = remote upload", "lightwhite", 'magenta') + ", " +\
        make_colors("s = sort by 'rel', 'name', 'date', 'size', 'timestamp'", 'r', "lw") + ", " +\
        make_colors("[n]e = Export n to file .csv", 'red', "lightyellow") + ", " +\
        make_colors('h|-h = Print command help', 'black', 'lightgreen') + ", " +\
        make_colors("e[x]it|[q]uit = exit|quit", 'lightred') + ", " +\
        make_colors("download_path=[dir], set download path", 'lightblue') + ", " +\
        make_colors("[n = Number selected] default select number is download n", 'lightwhite', 'lightblue') + ": "

        q = raw_input(note1)
        if q == 'q' or q == 'quit' or q == 'exit' or q == 'x':
            task = make_colors("EXIT", 'lightwhite', 'lightred')
            subtask = make_colors("System Exit !", 'lightwhite', 'lightred') + " "
            self.bar.update(self.max_value, task = task, subtask = subtask)            
            sys.exit(make_colors("System Exit !", 'lw', 'r'))
        return q		
    
    def build_dict(self, seq, key):
        data = dict((d[key], dict(d, index=index)) for (index, d) in enumerate(seq))
        debug(data_build_dict = data)
        return data
    
    def download_link(self, id_rel):
        if not self.check_cookies(self.sess.cookies).get('SID'):
            debug("login not use proxies")
            self.login()
        if not self.check_cookies(self.sess.cookies).get('SID'):
            debug("re login not use proxies")
            self.login(relogin = True)
        url = self.url + 'console/link.pl'
        if id_rel:
            data = {
                'selected[]':id_rel,
            }
            a = self.request(url, 'post', data=data)
                
            content = a.content
            b = bs(content, 'lxml')
            download_link = b.find('textarea').text
            debug(download_link = download_link)
            return download_link
        else:
            return False
    
    def export(self, id_rel, save_path = os.getcwd()):
        if not self.check_cookies(self.sess.cookies).get('SID'):
            debug("login not use proxies")
            self.login()
        if not self.check_cookies(self.sess.cookies).get('SID'):
            debug("re login not use proxies")
            self.login(relogin = True)
        url = self.url + 'console/fexp.pl'
        if id_rel:
            data = {
                            'selected[]':id_rel,
                        }
            a = self.request(url, 'post', data=data)
            content = a.content
            headers = a.headers
            filename = re.findall('filename=(.*?)\.csv', headers.get('content-disposition'))
            debug(filename = filename)
            filename = filename[0] + ".csv"
            if save_path:
                filename = os.path.join(save_path, filename)
            debug(filename = filename)
            b = bs(content, 'lxml')
            with open(filename, 'wb') as f:
                f.write(content)

            return filename
        else:
            return False
    
    def check_todo(self, proxy = None):
        proxies = self.build_proxy(proxy)
        if not self.check_cookies(self.sess.cookies).get('SID'):
            debug("login not use proxies")
            self.login()
        if not self.check_cookies(self.sess.cookies).get('SID'):
            debug("re login not use proxies")
            self.login(relogin = True)
        url = self.url + 'console/remote.pl?c=todo'
        a = self.request(url, proxies = proxies)
        b = bs(a.content, 'lxml')
        data = []
        ru_item = b.find_all('div', {'id':re.compile('d')})
        debug(ru_item = ru_item)
        if ru_item:
            for i in ru_item:
                div_url = i.find('div', {'class':'url'})
                debug(div_url = div_url)
                if div_url:
                    all_li = div_url.find('ul').find_all('li')
                    if all_li:
                        for x in all_li:
                            data.append(x.text)
            debug(data = data)
        return data
        #else:
            #sys.exit(make_colors("Check Todo -> No Data !", 'lightwhite', 'lightred', ['blink']))
    
    def date_to_timestamp(self, datetime_object):
        if sys.version_info.major == 3:
            return datetime_object.timestamp()
        else:
            return time.mktime(datetime_object.timetuple())
    
    def format_date(self, date, add = None, format_date = '%Y/%m/%d %H:%M'):
        fdate = datetime.strptime(date, format_date)
        year = fdate.year
        month = fdate.month
        day = fdate.day
        hour = fdate.hour
        minute = fdate.minute
        debug(year = year)
        debug(month = month)
        debug(day = day)
        debug(hour = hour)
        debug(minute = minute)
        if add:
            minute += add

        gdate = datetime(year, month, day, hour, minute)
        date_str = datetime.strftime(gdate, '%Y/%m/%d %H:%M')
        timestamp = self.date_to_timestamp(gdate)
        return date_str, timestamp
    
    def check_done(self, proxy = None):
        proxies = self.build_proxy(proxy)
        if not self.check_cookies(self.sess.cookies).get('SID'):
            debug("login not use proxies")
            self.login()
        if not self.check_cookies(self.sess.cookies).get('SID'):
            debug("re login not use proxies")
            self.login(relogin = True)
        url = self.url + 'console/remote.pl?c=done'
        a = self.request(url, proxies = proxies)
        b = bs(a.content, 'lxml')
        data = []
        alc = b.find('div', {'class':'alc'})
        debug(alc = alc)
        if alc and alc.text == "You don't have finished downloads":
            return data
        else:
            ru_item = b.find_all('div', {'class':'ru_item'})
            debug(ru_item = ru_item)
            for i in ru_item:
                asked_date = re.findall("Asked on (.*?)$", i.find('div').text)
                debug(asked_date = asked_date)
                li = i.find('ul').find('li')
                debug(li = li)
                status = None
                div_status = li.find('div')
                debug(div_status = div_status)
                if div_status:
                    status = div_status.text
                if status:
                    debug(status = status)
                    if "Download failed" in status:
                        # print(make_colors(status, 'lw', 'r'))
                        self.status_message = status
                        return "error"
                text = li.text
                debug(text = text)
                if text:
                    if "Download failed" in text:
                        return "error"
                    link = re.findall('.*?(https.*?)OK|.*?(http.*?)OK|.*?(ftp.*?)OK', text)
                    if link:
                        links = "".join(link[0])
                        debug(links = links)
                        size = re.findall('OK - (.*?) downloaded', text)
                        debug(size = size)
                        time_done = re.findall('downloaded in (.*?) ', text)
                        debug(time_done = time_done)
                        speed = re.findall('downloaded in .*? \((.*?)\)$', text)
                        debug(speed = speed)
                        data_add = {'link':links, 'size':size, 'time':time_done, 'speed':speed}
                        debug(data_add = data_add)
                        data.append(data_add)
            debug(data = data)
        return data
    
    def remove(self, id_rel, proxy = None):
        proxies = self.build_proxy(proxy)
        if not self.check_cookies(self.sess.cookies).get('SID'):
            debug("login not use proxies")
            self.login()
        if not self.check_cookies(self.sess.cookies).get('SID'):
            debug("re login not use proxies")
            self.login(relogin = True)
        url = self.url + 'console/remove.pl'
        data = {
            'remove':'1',
            'selected[]':id_rel
        }
        debug(data = data)
        a = self.request(url, 'post', data=data, proxies = proxies)
        content = a.content
        debug(content = content)
        if 'Files removed' in content:
            return True
        else:
            return False

    def _remove(self, number_selected, data, sort_by, bar, proxy = None):
        proxies = self.build_proxy(proxy)
        # if number_selected and str(number_selected).isdigit() and int(number_selected) <= len(data):
        debug(data_selected = data[int(number_selected) - 1])
        rel = data[int(number_selected) - 1].get('rel')
        name = unidecode(data[int(number_selected) - 1].get('name'))
        if name:
            if len(name) > 35:
                name = name[:35] + " ..."
        subtask = make_colors(name, 'lightwhite', 'blue') + " "
        task = make_colors("Deleting", "lightwhite", "lightred")
        self.bar.max_error = False
        self.bar.update(5, task = task, subtask = subtask)
        #raw_input("Enter to Continue")
        debug(rel = rel)
        self.remove(rel, proxy = proxies)
        self.bar.update(self.bar.max_value, task = task, subtask = subtask)
    
    def rename(self, id_rel, new_name, proxy = None):
        proxies = self.build_proxy(proxy)
        debug(proxies = proxies)
        if not self.check_cookies(self.sess.cookies).get('SID'):
            debug("login not use proxies")
            self.login()
        if not self.check_cookies(self.sess.cookies).get('SID'):
            debug("re login not use proxies")
            self.login(relogin = True)
        url = self.url + 'console/frename.pl'
        debug(url = url)
        data = {
            'newname': new_name,
            'file': id_rel
        }
        debug(data = data)
        a = self.request(url, 'post', data=data, proxies = proxies)
        content = a.content
        b = bs(content, 'lxml')
        with open('rename.html', 'wb') as ff:
            ff.write(content)
        debug(content = content)
        #pause()
        if 'File renamed successfully' in content:
            return True, ''
        else:
            self.report = b.find('div').text
            return False, b.find('div').text
    
    def remote_upload(self, links, timeout = 3, retries = 10, renameit = None, proxy = None):
        task = make_colors("Action", "lightwhite", "blue")
        subtask = make_colors("RemoteUpload", "lightwhite", "magenta") + " "        
        proxies = self.build_proxy(proxy)
        data, total = self.list()
        self.data = data
        self.status_message = None
        error = False
        if not self.check_cookies(self.sess.cookies).get('SID'):
            debug("login not use proxies")
            self.login()
        if not self.check_cookies(self.sess.cookies).get('SID'):
            debug("re login not use proxies")
            self.login(relogin = True)
        debug(cookie = self.sess.cookies)
        self.max_value = 100
        self.bar.max_value = 100
        self.clean_dones(proxy = proxies)
        url = self.url + 'console/remote.pl'
        for i in links:
            if i == 'c':
                i = clipboard.paste()
            if "http" == i[:4] and "://" in i[:10]:
                post_data = {'links': i }
                n = 1
                while 1:
                    try:
                        a = self.request(url, 'post', data = post_data, timeout = timeout, proxies = proxies)
                        break
                    except:
                        if not n == retries or n < retries:
                            n += 1
                            time.sleep(1)
                        elif n > retries:
                            n == retries                    
                        else:
                            error = True
                            break
                if error:
                    print(make_colors("please check internet connection !", 'lw', 'r'))
                    return False
                content = a.content
                # print("content =", content)
                print(make_colors(re.sub("<br/>", ": ", str(content)), 'lw', 'bl'))
                if "Can not find any valid link" in content:
                    print(make_colors("Can not find any valid link !", 'lightwhite', 'lightred'))
                    return False
                debug(content = content)
                check = re.findall('\d+ recorded links', content)
                debug(check = check)
                if check:
                    #bar = progressbar.ProgressBar(max_value = self.max_value, prefix = self.prefix, variables = self.variables)
                    
                    while 1:
                        data_done = self.check_done(proxy = proxies)
                        done = False
                        if data_done:
                            if data_done == 'error':
                                subtask = make_colors("RemoteUpload", "lightwhite", "magenta") + " " + make_colors("[{}]".format(self.status_message), 'lw', 'r') + " "
                                self.bar.update(self.max_value, task = task, subtask = subtask)
                                break
                            for j in data_done:
                                if j.get('link') == i:
                                    self.bar.update(self.max_value, task = task, subtask = subtask)
                                    done = True
                                    break
                            if done:
                                break
                        else:
                            if i in self.check_todo(proxy = proxies):
                                if self.bar.value == self.max_value:
                                    self.bar.value = 0							
                                self.bar.update(self.bar.value + 4, task = task, subtask = subtask)
                                time.sleep(2)
                            else:
                                if self.bar.value == self.max_value:
                                    self.bar.value = 0
                                self.bar.update(self.bar.value + 4, task = task, subtask = subtask)
                                time.sleep(2)
                else:
                    print(make_colors(content, 'lw', 'r'))
                    subtask = make_colors(content, 'lw', 'r') + " "
                    self.bar.update(self.bar.max_value, task = task, subtask = subtask)                    
                    #return False
                debug(renameit = renameit)
        
                if renameit:
                    all_prev_name = []
                    all_new_name = []
                    new_items = []
                    debug(self_data = self.data)
                    for i in self.data:
                        all_prev_name.append(i.get('name'))
                    data, total = self.list()
                    self.data = data
                    for i in self.data:
                        all_new_name.append(i.get('name'))
                    debug(all_prev_name = all_prev_name)
                    debug(all_new_name = all_new_name)
                    for name in all_new_name:
                        if not name in all_prev_name:
                            index = all_new_name.index(name)
                            new_items.append(self.data[index])
                    debug(new_items = new_items)
                    
                    if len(new_items) == 1:
                        status, info = self.rename(new_items[0].get('rel'), renameit[links.index(i)])
                        if status:
                            subtask = make_colors(renameit, 'lightwhite', 'blue') + " " + make_colors("[RENAME:SUCCESS]", 'b', 'lg') + " "    
                        else:
                            subtask = make_colors(renameit, 'lightwhite', 'blue') + " " + make_colors("[RENAME:ERROR:FAILED] [{}]".format(info), 'lw', 'r') + " "    
                        data, total = self.list()
                        self.data = data
            else:
                subtask = make_colors("Invalid URL:", 'lw', 'r') + " " + make_colors(i, 'b', 'y') + " "
                self.bar.update(self.bar.max_value, task = task, subtask = subtask)
                print(make_colors("Invalid URL:", 'lw', 'r') + " " + make_colors(i, 'b', 'y'))
                
        self.bar.update(self.bar.max_value, task = task, subtask = subtask)
        return True	
    
    def set_proxy(self, proxy):
        proxy_list = {}
        if isinstance(proxy, list):
            for i in proxy:
                if "{" in i[0]:
                    n = ast.literal_eval(i)
                    if isinstance(n, dict):
                        proxy_list.update(n)
                else:
                    j = urlparse(i)
                    scheme = j.scheme
                    debug(scheme = scheme)
                    if not scheme:
                        scheme = urlparse(self.url).scheme
                    debug(scheme = scheme)
                    netloc = j.netloc
                    if not netloc:
                        netloc = j.path
                    if "www." in netloc:
                        netloc = netloc.split('www.')[1]
                    #if ":" in netloc:
                        #netloc = netloc.split(":")[0]
                    proxy_list.update(
                        {
                            scheme:scheme + "://" + netloc,
                            'http': 'http://' + netloc,
                        }
                    )
        return proxy_list

    def usage(self):
        parser = argparse.ArgumentParser(formatter_class = argparse.RawTextHelpFormatter)
        parser.add_argument('-b', '--sort-by', action = 'store', help = 'Sortby: time/timestamp, date, name, rel, size', default = 'date')
        parser.add_argument('-r', '--remote-upload', action = 'store', help = 'Remote Upload, "c" = get url from clipboard ', nargs = '*')
        parser.add_argument('-n', '--rename', action = 'store', help = 'Rename after/or/and Remote Upload', nargs = "*")
        parser.add_argument('-p', '--download-path', action = 'store', help = 'Download Path or Export save path', default = os.getcwd())
        parser.add_argument('-d', '--download', action = 'store', help = 'Convert Link and download it or direct download with option "-nn"')
        parser.add_argument('-nn', '--ndownload', action = 'store', help = 'number of list to download', nargs='*')
        parser.add_argument('-g', '--generate', action = 'store', help = 'Convert Link Only')
        parser.add_argument('-C', '--clip', action = 'store', help = 'Convert Link and Copy to clipboard')
        parser.add_argument('-s', '--saveas', action = 'store', help = 'Download and Save as name')
        parser.add_argument('-w', '--wget', action = 'store_true', help = 'Force use wget as downloader')
        parser.add_argument('-c', '--confirm', action = 'store_true', help = 'Confirm before download it (IDM Only)')
        parser.add_argument('-U', '--username', action = 'store', help = 'Username (email) login')
        parser.add_argument('-P', '--password', action = 'store', help = 'Password login')
        parser.add_argument('-x', '--proxy', help="Via Proxy, example: https://192.168.0.1:3128 https://192.168.0.1:3128 ftp://127.0.0.1:33 or {'http':'127.0.0.1:8080', 'https': '10.5.6.7:5656'} or type 'auto' for auto proxy", action='store', nargs='*')
        parser.add_argument('-nv', '--no-verify', action = 'store_true', help = 'Use all type of proxy (http or https)')
        parser.add_argument('-a', '--all', action = 'store_true', help = 'Use all type of proxy (http or https) to session')
        parser.add_argument('-t', '--timeout', action = 'store', help = 'Connection timeout', default = 10)
        parser.add_argument('-http', '--http', action = 'store_true', help = 'Use all type of proxy (http or https) to session and set to http')
        parser.add_argument('-https', '--https', action = 'store_true', help = 'Use all type of proxy (http or https) to session and set to https')
        # if len(sys.argv) > 0:
            # print(make_colors("use '-h' for Command Help", 'lightred', 'lightwhite'))
        #     self.navigator()
        # else:
        args = parser.parse_args()
        proxy = {}
        scheme = urlparse(self.url).scheme

        self.timeout = args.timeout

        if self.config.get_config('proxy', scheme):
            #proxy = {scheme: scheme + "://" + self.conf.get_config('proxy', scheme),}
            proxy = {scheme: self.config.get_config('proxy', scheme),}
        if args.proxy:
            debug(args_proxy = args.proxy)
            proxy = self.set_proxy(args.proxy)
            debug(proxy = proxy)
            self.sess.proxies = proxy
        if args.remote_upload:
            if args.remote_upload == ["c"]:
                args.remote_upload = [clipboard.paste()]
            self.remote_upload(args.remote_upload, renameit = args.rename)
            self.refresh(args.sort_by)
        if args.download or args.generate:
            if args.download:
                data = self.get_download_link(args.download)
            elif args.generate:
                data = self.get_download_link(args.generate)
            if data[0]:
                url_download = data[1]
                print("\n")
                print(make_colors("GENERATED :", 'lw', 'r') + " " + make_colors(url_download, 'y'))
                print(make_colors("NAME      :", 'b', 'c')  + " " + make_colors(data[2].get('name'), 'c'))
                print(make_colors("SIZE      :", 'b', 'y')  + " " + make_colors(data[2].get('size'), 'g'))
                print(make_colors("DATE      :", 'lw', 'm') + " " + make_colors(data[2].get('date'), 'bl'))

                if args.clip:
                    clipboard.copy(url_download)
                if args.download:
                    self.download(url_download, args.download_path, args.confirm, args.wget, args.saveas)
        if args.ndownload:
            self.navigator(args.username, args.password, args.no_verify, args.all, args.https, args.http, args.proxy, None, args.download_path, args.confirm, args.wget, None, None, False, args.sort_by, args.ndownload)
        else:
            print("\n")
            self.navigator(args.username, args.password, args.no_verify, args.all, args.https, args.http, proxy, download_path = args.download_path, confirm = args.confirm, force_wget = args.wget, sort_by = args.sort_by, direct_download_number=args.ndownload)

def usage():
    c = onefichier()
    c.usage()
    
if __name__ == '__main__':
    c = onefichier()
    c.usage()
    #c.remove("C_0_g38aio8euw61hrvjvxw5")
    # c.get_download_link(sys.argv[1])
    # c.get_download_link("https://1fichier.com/?13tkjkqtegzxu5ilewnl")
    #.get_download_link("https://1fichier.com/?vmq3xfyq9rzl5hm68d68")
    #c.login()
    #c.list()
    #dl = c.download_link("C_0_13tkjkqtegzxu5ilewnl")
    #c.export("C_0_13tkjkqtegzxu5ilewnl")
    #c.remote_upload(sys.argv[1:])
    #c.check_done()
    #if dl:
    #	link = c.get_download_link(dl)
    #	debug(link = link)
