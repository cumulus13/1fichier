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
if sys.version_info.major == 3:
    raw_input = input
    from urllib.parse import urlparse
else:
    from urlparse import urlparse
import ast
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
        self.configname = os.path.join(os.path.dirname(__file__), '1fichier.ini')
        self.config = configset(self.configname)
        self.sess = requests.Session()
        self.logined = False

        self.prefix = '{variables.task} >> {variables.subtask}'
        self.variables =  {'task': '--', 'subtask': '--'}
        self.max_value = 10
        self.status_message = ""
        self.data = ''
        self.total = 0

    def set_header(self, header_str = None):
        """generate mediafire url to direct download url

        Args:
            header_str (str, optional): raw headers data/text from browser on development mode

        Returns:
            TYPE: dict: headers data
        """

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

    def request(self, url, rtype = 'get', headers = None, data = {}, params = {}, timeout = 3, retries = 10, sleep = 1):
        timeout = timeout or self.config.get_config('policy', 'timeout', '10')
        debug(timeout = timeout)
        retries = retries or self.config.get_config('policy', 'retries', '10')
        debug(retries = retries)
        sleep = sleep or self.config.get_config('policy', 'sleep', '1')
        debug(sleep = sleep)
        n = 1
        error = False
        error_type = ''
        error_full = ''
        if not headers:
            headers = self.set_header()
        debug(headers = headers)
        
        while 1:
            try:
                if rtype == 'post':    
                    req = self.sess.post(url, data=data, params = params, headers = headers, timeout = timeout)
                else:
                    req = self.sess.get(url, params = params, headers = headers, timeout = timeout)
                break
            except:
                tr, vl, tb = sys.exc_info()
                error_type = vl.__class__.__name__
                error_full = traceback.format_exc()
                if not n == retries:
                    n += 1
                    time.sleep(sleep)
                else:
                    error = True
                    break
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
    
    def login(self, username=None, password=None, url_code = 'login.pl'):
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
        a = self.request(url, data = data, rtype = 'post')
        if not a:
            print(make_colors("Login Failed !", 'lw', 'r'))
            sys.exit()
        debug(sess_proxy = self.sess.proxies)
        content = a.content
        b = bs(content, 'lxml')
        bloc = b.find('div', {'class':'bloc2'})
        debug(bloc =  bloc)
        if bloc and "temporarily locked" in bloc.text:
            if self.logined:
                debug(login = "return False")
                return False
            else:
                print(make_colors(bloc.text, 'lightwhite', 'lightred'))
                self.logined = True
                self.auto_proxy()
        #print("content =", content)
        debug(content = content)
        cookies_0 = a.cookies
        cookies_1 = self.sess.cookies
        debug(cookies_0 = cookies_0)
        debug(cookies_1 = cookies_1)
        return True
    
    def auto_proxy(self, no_verify = False, use_all = False, force_https = False, force_http = False, proxy = {}):
        scheme = urlparse(self.url).scheme
        from proxy_tester import proxy_tester
        import warnings
        warnings.filterwarnings("ignore")
        pc = proxy_tester.proxy_tester()
        n_try = 1
        list_proxy = pc.getProxyList()
        proxies = {}
        bar = progressbar.ProgressBar(max_value = self.max_value, prefix = self.prefix, variables = self.variables)
        if not proxy:
            while 1:
                bar.max_value = len(list_proxy)
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
                        bar.update(n_try, task = make_colors("Check Proxy", 'black', 'lightgreen'), subtask = make_colors(i.get('ip') + ":" + i.get('port'), 'lightwhite', 'lightblue') + " ")
                        try:
                            requests.request('GET', self.url, proxies=proxies, verify=False, timeout=3)
                            debug(proxies = proxies)
                            #print("\n")
                            #print(make_colors("Use proxy: ", 'lightyellow') + make_colors(proxies.get(scheme), 'lightwhite', 'blue'))
                            bar.update(n_try, task = make_colors("Try Proxy", 'lightwhite', 'lightred'), subtask = make_colors(proxy_str, 'lightwhite', 'lightblue') + " ")
                            self.sess.proxies = proxies
                            c = self.login()
                            if c:
                                break

                        except:
                            bar.max_value = len(list_proxy)
                            bar.value = n_try

                        debug(n_try = n_try)
                        if n_try == len(list_proxy):
                            break
                        else:
                            n_try += 1                            
                    else:
                        if scheme == 'https' and i.get('https') == 'yes':
                            proxies = {scheme: str(scheme + "://" + i.get('ip') + ":" + i.get('port')),}
                            bar.update(n_try, task = make_colors("Match Proxy", 'black', 'lightgreen'), subtask = make_colors(proxies.get(scheme), 'lightwhite', 'lightblue') + " ")
                            try:
                                requests.request('GET', self.url, proxies=proxies, verify=False, timeout=3)
                                #print("\n")
                                #print(make_colors("Use proxy: ", 'lightyellow') + make_colors(proxies.get(scheme), 'lightwhite', 'blue'))
                                bar.update(n_try, task = make_colors("Try Proxy", 'lightwhite', 'lightred'), subtask = make_colors(proxies.get(scheme), 'lightwhite', 'lightblue') + " ")
                                debug(proxies = proxies)
                                self.sess.proxies = proxies
                                c = self.login()
                                if c:
                                    break
                            except:
                                bar.max_value = len(list_proxy)
                                bar.value = n_try
                        else:
                            bar.value + 1
                        debug(n_try = n_try)
                        if n_try == len(list_proxy):
                            break
                        else:
                            n_try += 1


                if n_try == len(list_proxy):
                    bar.finish()
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
            bar.max_value = 100
            c = self.login()
            if not c:
                bar.update(100, task = make_colors("ERROR", 'lightwhite', 'lightred'), subtask = make_colors("[ERROR CONNECTION]", 'lightred', 'lightyellow') + " ")
                sys.exit(make_colors("[ERROR CONNECTION]", 'lightwhite', 'lightred') + make_colors('Try Again !', 'black', 'lightyellow'))
        return proxies
    
    def clean_dones(self):
        if not self.sess.cookies.get('SID'):
            self.login()
        url = self.url + "console/remote.pl?r=all"
        return self.request(url)
    
    def get_download_link_info(self, bs_object = None, url = None):
        if not bs_object:
            if url:
                a = self.request(url)
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
    
    def get_download_link(self, url, print_wait = True):
        warn_minutes = False
        info = {}
        
        if not self.sess.cookies.get('SID'):
            self.login()
        a = self.request(url)
        if not a:
            print(make_colors("Get download link [1] Failed !", 'lw', 'r'))
        b = bs(a.content, 'lxml')
        hidden = b.find('input', {'type':'hidden'})
        debug(hidden = hidden)
        data = {'adz':hidden.get('value')}
        a1 = self.request(url, 'post', data=data)
        if not a1:
            print(make_colors("Get download link [2] Failed !", 'lw', 'r'))
            return False, warn_minutes, info
        content = a1.content
        # debug(content = content)
        b1 = bs(content, 'lxml')
        #debug(b1 = b1)
        link = b1.find('a', text=re.compile('Click here to download the file'))
        warn = b1.find_all('div', {'class':"ct_warn"})
        debug(warn = warn)
        debug(link = link)
        if link:
            info = self.get_download_link_info(b, url)
            if not info:
                info = self.get_download_link_info(b1, url)
            debug(download_link = link.get('href'))
            debug(info = info)
            return True, link.get('href'), info
        else:
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
                    warning = re.sub("  ", " ", warning)
                    warning = re.sub("  ", " ", warning)
                    warning = re.sub("  ", " ", warning)
                    warning = re.sub("\n", " ", warning)
                    warning = re.sub("\r", "", warning)
                    if print_wait:
                        print(make_colors(warning, 'lightwhite', 'lightred', ['blink']))
                    if str(warn_minutes).isdigit() and int(warn_minutes) > 1:
                        time.sleep(60)
                        if print_wait:
                            print(make_colors("waiting for: 1 minute", 'lightwhite', 'lightred', ['blink']))
                        return self.get_download_link(url) 
                    elif str(warn_minutes).isdigit() and int(warn_minutes) <= 1:
                        time.sleep(2)
                        if print_wait:
                            print(make_colors("waiting for: 2 seconds for {} minutes".format(warn_minutes), 'lightwhite', 'lightred', ['blink']))
                        sys.stdout.write(".")
                        sys.stdout.flush()
                        return self.get_download_link(url, False) 
                return False, warn_minutes, info

        return False, warn_minutes, info
    
    def list(self):
        if not self.sess.cookies.get('SID'):
            self.login()
        data = []
        url = self.url + 'console/files.pl?dir_id=0&oby=0&search='
        a = self.request(url)
        debug(url = a.url)
        content = a.content
        debug(content = content)
        debug(SID = self.sess.cookies.get('SID'))
        b = bs(content, 'lxml')
        sable = b.find('ul', {'id':'sable'}).find_all('li')
        debug(sable = sable)
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

    def refresh(self):
        data, total = self.list()
        self.data = data
        self.total = total
    
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

    def navigator(self, username = None, password = None, no_verify = False, use_all = False, force_https = False, force_http = False, proxy = {}, minute_add = None, download_path = os.getcwd(), confirm = False, force_wget = False, q = None, data = None, print_list = True, sort_by = 'date', direct_download_number = None):
        check_sort_by = ['rel', 'name', 'date', 'size', 'timestamp']
        total = 0
        data1 = {}
        if not self.sess.cookies.get('SID'):
            self.login(username, password)
        debug(sort_by = sort_by)
        debug(data = data)
        if self.data:
            data = self.data
        debug(data = data)
        
        if not data:
            data, total = self.list()
            debug(data = data)
            if str(sort_by).lower().strip() == 'time':
                sort_by = 'timestamp'
            if sort_by and sort_by in check_sort_by:
                debug(sort_by = sort_by)
                data1 = self.build_dict(data, key = str(sort_by))			
                data = sorted(data, key=lambda y: y.get(sort_by))
                debug(data = data)
        else:
            self.data = data
            debug("data is it")
            if sort_by:
                debug(sort_by = sort_by)
                
                data, total = self.list()
                if str(sort_by).lower().strip() == 'time':
                    sort_by = 'timestamp'
                if sort_by and sort_by in check_sort_by:
                    if sort_by == 'size':
                        data1 = self.build_dict(data, key = str(sort_by))           
                        data = sorted(data, key=lambda y: bitmath.parse_string_unsafe(y.get(sort_by)).kB.value)
                else:
                    data1 = self.build_dict(data, key = str(sort_by))           
                    data = sorted(data, key=lambda y: y.get(sort_by))
        
        
        debug(data = data)			
        
        debug(print_list = print_list)
        if print_list and data:
            n = 1
            for i in data:
                if len(str(n)) == 1:
                    number = "0" + str(n)
                else:
                    number = str(n)
                # if sort_by and str(sort_by).lower().strip() in data1.get(list(data1.keys())[0]).keys():
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
        bar = progressbar.ProgressBar(max_value = self.max_value, prefix = self.prefix, variables = self.variables)
        
        if q:
            q = str(q).strip()
            if q and str(q).isdigit() and int(q) <= len(data):
                debug("q is digit")
                task = make_colors("Download Link", 'lightwhite', 'blue')
                subtask = make_colors("Get", 'lightwhite', 'magenta') + " "
                bar.update(bar.value + 1, task = task, subtask = subtask)
                #print("data.get(list(data.keys())[0]).keys() =", data.get(list(data.keys())[0]).keys())
                if sort_by and str(sort_by).lower().strip() in data.get(list(data.keys())[0]).keys():
                    debug(data_selected = data.get(list(data.keys())[int(q) - 1]))
                    link = self.download_link(data.get(list(data.keys())[int(q) - 1]).get('rel'))
                    name = data.get(list(data.keys())[int(q) - 1]).get('name')
                else:
                    link = self.download_link(data[int(q) - 1].get('rel'))
                    name = data[int(q) - 1].get('name')

                task = make_colors("Generator", 'lightwhite', 'blue')
                subtask = make_colors("Convert", 'lightwhite', 'magenta') + " "
                bar.update(bar.value + 1, task = task, subtask = subtask)
                download_link = self.get_download_link(link)
                if download_link[0]:
                    print(make_colors("GENERATE:", 'r', 'lw') + " " + make_colors(download_link[1], 'b', 'ly'))
                    print(make_colors("NAME    :", 'lw', 'bl') + " " + make_colors(download_link[2].get('name'), 'lw', 'bl'))
                    print(make_colors("SIZE    :", 'b', 'lg') + " " + make_colors(download_link[2].get('size'), 'b', 'lg'))
                    print(make_colors("DATE    :", 'lw', 'm') + " " + make_colors(download_link[2].get('date'), 'lw', 'm'))
                else:
                    print(make_colors("GENERATE:", 'r', 'lw') + " " + make_colors("FAILED !", 'lw', 'r'))
            elif q and q[-1:] == 'd' and q[:-1].isdigit():
                debug("q containt 'd'")
                q = q[:-1]
                task = make_colors("Download Link", 'lightwhite', 'blue')
                subtask = make_colors("Get", 'lightwhite', 'magenta') + " "
                bar.update(bar.value + 1, task = task, subtask = subtask)
                #print("data.get(list(data.keys())[0]).keys() =", data.get(list(data.keys())[0]).keys())
                if sort_by and str(sort_by).lower().strip() in data.get(list(data.keys())[0]).keys():
                    debug(data_selected = data.get(list(data.keys())[int(q) - 1]))
                    link = self.download_link(data.get(list(data.keys())[int(q) - 1]).get('rel'))
                    name = data.get(list(data.keys())[int(q) - 1]).get('name')
                else:
                    link = self.download_link(data[int(q) - 1].get('rel'))
                    name = data[int(q) - 1].get('name')

                task = make_colors("Download Link", 'lightwhite', 'blue')
                subtask = make_colors("Convert", 'lightwhite', 'magenta') + " "
                bar.update(bar.value + 1, task = task, subtask = subtask)
                download_link = self.get_download_link(link)
                debug(download_link = download_link)
                task = make_colors("Download", 'lightwhite', 'blue')
                subtask = make_colors(name, 'lightred', 'lightyellow') + " "
                bar.update(bar.value + 1, task = task, subtask = subtask)
                print(make_colors("DOWNLOAD LINK:", 'b', 'y') + " " + make_colors(download_link[1], 'b', 'c'))
                if download_link[0]:
                    self.download(download_link[1], download_path, confirm, force_wget, name)
                else:
                    task = make_colors("Download", 'lightwhite', 'lightred')
                    subtask = make_colors("ERROR Wait for " + download_link[1] + " minutes", 'lightred', 'lightwhite') + " "
                bar.update(bar.max_value, task = task, subtask = subtask)					
            elif q and q[-1:] == 'm' and q[:-1].isdigit():
                debug("q containt 'm'")
                if len(str(q).strip()) > 1:
                    number_selected = str(q).strip()[:-1]
                else:
                    number_selected = raw_input(make_colors("Select number to remove: ", 'lightwhite', 'lightred'))

                if number_selected and str(number_selected).isdigit() and int(number_selected) <= len(data):
                    self._remove(number_selected, data, sort_by, bar)
                    self.refresh()

                elif "," in number_selected or " " in number_selected:
                    number_selected = re.sub(" ", "", number_selected)
                    list_number_selected = re.split(",| ", number_selected)
                    debug(list_number_selected = list_number_selected)
                    for i in list_number_selected:
                        bar.max_value = len(list_number_selected)
                        number_selected = str(i).strip()
                        if number_selected and str(number_selected).isdigit() and int(number_selected) <= len(data):
                            self._remove(number_selected, data, sort_by, bar)
                        else:
                            task = make_colors("Deleting", "lightwhite", "lightred")
                            subtask = make_colors("ERROR", 'lightwhite', 'lightred') + " "
                            bar.update(bar.value + 1, task = task, subtask = subtask)

                elif "-" in number_selected:
                    number_selected = re.sub(" ", "", number_selected)
                    debug(number_selected = number_selected)
                    number_selected = re.split("-", number_selected)
                    debug(number_selected = number_selected)
                    list_number_selected = list(range(int(number_selected[0]), (int(number_selected[1]) + 1)))
                    debug(list_number_selected = list_number_selected)
                    # list_number_selected_str = str(list_number_selected)[1:-1] + "m"
                    # debug(list_number_selected_str = list_number_selected_str)
                    for i in list_number_selected:
                        bar.max_value = len(list_number_selected)
                        number_selected = str(i).strip()
                        if number_selected and str(number_selected).isdigit() and int(number_selected) <= len(data):
                            self._remove(number_selected, data, sort_by, bar)
                        else:
                            task = make_colors("Deleting", "lightwhite", "lightred")
                            subtask = make_colors("ERROR", 'lightwhite', 'lightred') + " "
                            bar.update(bar.value + 1, task = task, subtask = subtask)
                    # return self.navigator(username, password, no_verify, use_all, force_https, force_http, proxy, minute_add, download_path, confirm, force_wget, list_number_selected_str, data, False, sort_by = sort_by)
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
                        if sort_by and str(sort_by).lower().strip() in data.get(list(data.keys())[0]).keys():
                            debug(data_selected = data.get(list(data.keys())[int(number_selected) - 1]))
                            rel = data.get(list(data.keys())[int(number_selected) - 1]).get('rel')
                            subtask = make_colors(new_name, 'lightwhite', 'blue') + " "
                        else:
                            rel = data[int(number_selected) - 1].get('rel')
                            subtask = make_colors(new_name, 'lightwhite', 'blue') + " "
                        task = make_colors("Rename to", "lightwhite", "lightred")                        
                        bar.update(5, task = task, subtask = subtask)
                        #raw_input("Enter to Continue")
                        debug(rel = rel)
                        self.rename(rel, new_name)
                        bar.update(bar.max_value, task = task, subtask = subtask)
            elif q and q[-1:] == 'e' and q[:-1].isdigit():
                debug("q containt 'e'")
                if len(str(q).strip()) > 1:
                    number_selected = str(q).strip()[:-1]
                else:
                    number_selected = raw_input(make_colors("Select number to export: ", 'lightwhite', 'lightred'))
                task = make_colors("Export", "lightwhite", "blue")
                subtask = make_colors("start", 'black', 'lightgreen') + " "
                bar.update(bar.value + 5, task = task, subtask = subtask)
                if number_selected and str(number_selected).isdigit() and int(number_selected) <= len(data):
                    if sort_by and str(sort_by).lower().strip() in data.get(list(data.keys())[0]).keys():
                        debug(data_selected = data.get(list(data.keys())[int(number_selected) - 1]))
                        rel = data.get(list(data.keys())[int(number_selected) - 1]).get('rel')
                        subtask = make_colors(data.get(list(data.keys())[int(number_selected) - 1]).get('name'), 'lightwhite', 'blue') + " "
                    else:
                        debug(data_selected = data[int(number_selected) - 1])
                        rel = data[int(number_selected) - 1].get('rel')
                        subtask = make_colors(data[int(number_selected) - 1].get('name'), 'lightwhite', 'blue') + " "
                else:
                    task = make_colors("Export", "lightwhite", "lightred")
                    subtask = make_colors("ERROR", 'lightwhite', 'lightred') + " "
                    bar.update(bar.max_value, task = task, subtask = subtask)

                task = make_colors("Export", "lightwhite", "blue")
                debug(rel = rel)
                self.export(rel, download_path)
                bar.update(bar.max_value, task = task, subtask = subtask)
            elif q == 'r':
                debug("q is 'r'")
                qr = raw_input(make_colors("Input Remote URL: ", 'lightwhite', 'blue'))
                if qr:
                    if qr.strip() == 'c':
                        qr = clipboard.paste()
                    if 'http' in qr or 'ftp' in qr:
                        self.remote_upload(str(qr))
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
                bar.update(self.max_value, task = task, subtask = subtask)
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
        self.refresh()
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
        return q		
    
    def build_dict(self, seq, key):
        data = dict((d[key], dict(d, index=index)) for (index, d) in enumerate(seq))
        debug(data_build_dict = data)
        return data
    
    def download_link(self, id_rel):
        if not self.sess.cookies.get('SID'):
            self.login()
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
        if not self.sess.cookies.get('SID'):
            self.login()
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
    
    def check_todo(self):
        if not self.sess.cookies.get('SID'):
            self.login()
        url = self.url + 'console/remote.pl?c=todo'
        a = self.request(url)
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
    
    def check_done(self):
        if not self.sess.cookies.get('SID'):
            self.login()
        url = self.url + 'console/remote.pl?c=done'
        a = self.request(url)
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
    
    def remove(self, id_rel):
        if not self.sess.cookies.get('SID'):
            self.login()
        url = self.url + 'console/remove.pl'
        data = {
                    'remove':'1',
                        'selected[]':id_rel
                }
        debug(data = data)
        a = self.request(url, 'post', data=data)
        content = a.content
        debug(content = content)
        if 'Files removed' in content:
            return True
        else:
            return False

    def _remove(self, number_selected, data, sort_by, bar):
        # if number_selected and str(number_selected).isdigit() and int(number_selected) <= len(data):
        if sort_by and str(sort_by).lower().strip() in data.get(list(data.keys())[0]).keys():
            debug(data_selected = data.get(list(data.keys())[int(number_selected) - 1]))
            rel = data.get(list(data.keys())[int(number_selected) - 1]).get('rel')
            name = unidecode(data.get(list(data.keys())[int(number_selected) - 1]).get('name'))
            subtask = make_colors(name, 'lightwhite', 'blue') + " "
        else:
            rel = data[int(number_selected) - 1].get('rel')
            name = unidecode(data[int(number_selected) - 1].get('name'))
            subtask = make_colors(name, 'lightwhite', 'blue') + " "
        task = make_colors("Deleting", "lightwhite", "lightred")                        
        bar.update(5, task = task, subtask = subtask)
        #raw_input("Enter to Continue")
        debug(rel = rel)
        self.remove(rel)
        bar.update(bar.max_value, task = task, subtask = subtask)
    
    def rename(self, id_rel, new_name):
        if not self.sess.cookies.get('SID'):
            self.login()
        url = self.url + 'console/frename.pl'
        data = {
            'newname': new_name,
            'file': id_rel
        }
        debug(data = data)
        a = self.request(url, 'post', data=data)
        content = a.content
        debug(content = content)
        if 'File renamed successfully' in content:
            return True
        else:
            return False
    
    def remote_upload(self, links, timeout = 3, retries = 10, renameit = None):
        data, total = self.list()
        self.data = data
        self.status_message = None
        error = False
        if not self.sess.cookies.get('SID'):
            self.login()
        debug(cookie = self.sess.cookies)
        self.max_value = 100
        self.clean_dones()
        url = self.url + 'console/remote.pl'
        for i in links:
            if i == 'c':
                i = clipboard.paste()
            post_data = {'links': i }
            n = 1
            while 1:
                try:
                    a = self.request(url, 'post', data = post_data, timeout = timeout)
                    break
                except:
                    if not n == retries:
                        n += 1
                        time.sleep(1)
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
                bar = progressbar.ProgressBar(max_value = self.max_value, prefix = self.prefix, variables = self.variables)
                task = make_colors("Action", "lightwhite", "blue")
                subtask = make_colors("RemoteUpload", "lightwhite", "magenta") + " "
                while 1:
                    data_done = self.check_done()
                    done = False
                    if data_done:
                        if data_done == 'error':
                            subtask = make_colors("RemoteUpload", "lightwhite", "magenta") + " " + make_colors("[{}]".format(self.status_message), 'lw', 'r') + " "
                            bar.update(self.max_value, task = task, subtask = subtask)
                            break
                        for j in data_done:
                            if j.get('link') == i:
                                bar.update(self.max_value, task = task, subtask = subtask)
                                done = True
                                break
                        if done:
                            break
                    else:
                        if i in self.check_todo():
                            if bar.value == self.max_value:
                                bar.value = 0							
                            bar.update(bar.value + 4, task = task, subtask = subtask)
                            time.sleep(2)
                        else:
                            if bar.value == self.max_value:
                                bar.value = 0
                            bar.update(bar.value + 4, task = task, subtask = subtask)
                            time.sleep(2)
            else:
                return False
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
                self.rename(new_items[0].get('rel'), renameit)
                data, total = self.list()
                self.data = data
        
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
        parser.add_argument('-b', '--sort-by', action = 'store', help = 'Sortby: time/timestamp, date, name, rel, size', default = 'time')
        parser.add_argument('-r', '--remote-upload', action = 'store', help = 'Remote Upload, "c" = get url from clipboard ', nargs = '*')
        parser.add_argument('-n', '--rename', action = 'store', help = 'Rename after/or/and Remote Upload')
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
        parser.add_argument('-http', '--http', action = 'store_true', help = 'Use all type of proxy (http or https) to session and set to http')
        parser.add_argument('-https', '--https', action = 'store_true', help = 'Use all type of proxy (http or https) to session and set to https')
        if len(sys.argv) == 1:
            print(make_colors("use '-h' for Command Help", 'lightred', 'lightwhite'))
            self.navigator()
        else:
            args = parser.parse_args()
            proxy = {}
            scheme = urlparse(self.url).scheme
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
                self.refresh()
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
    # c.get_download_link("https://1fichier.com/?13tkjkqtegzxu5ilewnl")
    # c.get_download_link("https://1fichier.com/?vmq3xfyq9rzl5hm68d68")
    #c.login()
    #c.list()
    #dl = c.download_link("C_0_13tkjkqtegzxu5ilewnl")
    #c.export("C_0_13tkjkqtegzxu5ilewnl")
    #c.remote_upload(sys.argv[1:])
    #c.check_done()
    #if dl:
    #	link = c.get_download_link(dl)
    #	debug(link = link)
