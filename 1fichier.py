#!c:/SDK/Anaconda2/python.exe
#~*~*encode:utf-8*~*~
#~*~*encoding:utf-8*~*~
from __future__ import print_function
import os, sys
import requests
from bs4 import BeautifulSoup as bs
import argparse
from make_colors import make_colors
from pydebugger.debug import debug
from configset import configset
import progressbar
from idm import IDMan
from pywget import wget
import clipboard
import re
import traceback
import time
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
	import getch

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
		
		a = self.sess.post(url, data = data)
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
		return self.sess.get(url)
	
	def get_download_link(self, url):
		if not self.sess.cookies.get('SID'):
			self.login()
		a = self.sess.get(url)
		b = bs(a.content, 'lxml')
		hidden = b.find('input', {'type':'hidden'})
		debug(hidden = hidden)
		data = {
			'adz':hidden.get('value')
		}
		a1 = requests.post(url, data=data)
		content = a1.content
		debug(content = content)
		b1 = bs(content, 'lxml')
		#debug(b1 = b1)
		link = b1.find('a', text=re.compile('Click here to download the file'))
		warn = b1.find_all('div', {'class':"ct_warn"})
		debug(warn = warn)
		debug(link = link)
		warn_minutes = False
		if link:
			debug(download_link = link.get('href'))
			return True, link.get('href')
		else:
			if warn:
				warning = warn[1].text
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
					print(make_colors(warning, 'lightwhite', 'lightred', ['blink']))
				return False, warn_minutes
		
		return False, warn_minutes
		
	def list(self):
		if not self.sess.cookies.get('SID'):
			self.login()
		data = []
		url = self.url + 'console/files.pl?dir_id=0&oby=0&search='
		a = self.sess.get(url)
		debug(url = a.url)
		content = a.content
		debug(content = content)
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
	
	def download(self, url, download_path=os.getcwd(), confirm=False, use_wget=False, name = None):
		if use_wget:
			wget.download(url, download_path)
		else:
			try:
				idm = IDMan()
				idm.download(url, download_path, name, confirm=confirm)
			except:
				traceback.format_exc()
				if name:
					download_path = os.path.join(download_path, name)
				wget.download(url, download_path)
	
	def navigator(self, username = None, password = None, no_verify = False, use_all = False, force_https = False, force_http = False, proxy = {}, minute_add = None, download_path = os.getcwd(), confirm = False, force_wget = False, q = None, data = None, print_list = True, sort_by = None):
		check_sort_by = ['rel', 'name', 'date', 'size', 'timestamp']
		if not self.sess.cookies.get('SID'):
			self.login(username, password)
		debug(sort_by = sort_by)
		if not data:
			data, total = self.list()
			if str(sort_by).lower().strip() == 'time':
				sort_by = 'timestamp'
			if sort_by and sort_by in check_sort_by:
				debug(sort_by = sort_by)
				data = self.build_dict(data, key = str(sort_by))			

		if data:
			debug(data = data)			
			if print_list:
				n = 1
				for i in data:
					if len(str(n)) == 1:
						number = "0" + str(n)
					else:
						number = str(n)
					if sort_by and str(sort_by).lower().strip() in data.get(list(data.keys())[0]).keys():
						print(make_colors(number, 'lightcyan') + ". " + make_colors(data.get(i).get('name'), 'lightwhite', 'lightblue') + " [" + make_colors(data.get(i).get('size'), 'black', 'lightgreen') + "] [" + make_colors(data.get(i).get('date'), 'lightwhite', 'magenta') + "]")
					else:
						print(make_colors(number, 'lightcyan') + ". " + make_colors(i.get('name'), 'lightwhite', 'lightblue') + " [" + make_colors(i.get('size'), 'black', 'lightgreen') + "] [" + make_colors(i.get('date'), 'lightwhite', 'magenta') + "]")
					n += 1
				print(make_colors("TOTAL Size:", 'lw', 'b') + " " + make_colors(str(total) , 'b', 'lg'))
			if not q:
				q = self.print_nav()
			bar = progressbar.ProgressBar(max_value = self.max_value, prefix = self.prefix, variables = self.variables)
			if q:
				q = str(q).strip()
			if q and str(q).isdigit() and int(q) <= len(data):
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
				task = make_colors("Download", 'lightwhite', 'blue')
				subtask = make_colors(name, 'lightred', 'lightyellow') + " "
				bar.update(bar.value + 1, task = task, subtask = subtask)
				if download_link[0]:
					self.download(download_link[1], download_path, confirm, force_wget, name)
				else:
					task = make_colors("Download", 'lightwhite', 'lightred')
					subtask = make_colors("ERROR Wait for " + download_link[1] + " minutes", 'lightred', 'lightwhite') + " "
					bar.update(bar.max_value, task = task, subtask = subtask)					
				
			elif str(q).strip()[-1] == 'm':
				if len(str(q).strip()) > 1:
					number_selected = str(q).strip()[:-1]
				else:
					number_selected = raw_input(make_colors("Select number to remove: ", 'lightwhite', 'lightred'))
					
				if number_selected and str(number_selected).isdigit() and int(number_selected) <= len(data):
					if sort_by and str(sort_by).lower().strip() in data.get(list(data.keys())[0]).keys():
						debug(data_selected = data.get(list(data.keys())[int(number_selected) - 1]))
						rel = data.get(list(data.keys())[int(number_selected) - 1]).get('rel')
						subtask = make_colors(data.get(list(data.keys())[int(number_selected) - 1]).get('name'), 'lightwhite', 'blue') + " "
					else:
						rel = data[int(number_selected) - 1].get('rel')
						subtask = make_colors(data[int(number_selected) - 1].get('name'), 'lightwhite', 'blue') + " "
					task = make_colors("Deleting", "lightwhite", "lightred")						
					bar.update(5, task = task, subtask = subtask)
					#raw_input("Enter to Continue")
					debug(rel = rel)
					self.remove(rel)
					bar.update(bar.max_value, task = task, subtask = subtask)
					
				elif "," in number_selected or " " in number_selected:
					number_selected = re.sub(" ", "", number_selected)
					list_number_selected = re.split(",| ", number_selected)
					debug(list_number_selected = list_number_selected)
					for i in list_number_selected:
						bar.max_value = len(list_number_selected)
						number_selected = str(i).strip()
						if number_selected and str(number_selected).isdigit() and int(number_selected) <= len(data):
							#print("str(sort_by).lower().strip() =", str(sort_by).lower().strip())
							#print("data.get(list(data.keys())[0]).keys() =", data.get(list(data.keys())[0]).keys())
							if sort_by and str(sort_by).lower().strip() in data.get(list(data.keys())[0]).keys():
								debug(data_selected = data.get(list(data.keys())[int(number_selected) - 1]))
								rel = data.get(list(data.keys())[int(number_selected) - 1]).get('rel')
								subtask = make_colors(data.get(list(data.keys())[int(number_selected) - 1]).get('name'), 'lightwhite', 'blue') + " "
							else:
								rel = data[int(number_selected) - 1].get('rel')
								subtask = make_colors(data[int(number_selected) - 1].get('name'), 'lightwhite', 'blue') + " "
								
							task = make_colors("Deleting", "lightwhite", "lightred")
							debug(rel = rel)
							self.remove(rel)
							bar.update(bar.value + 1, task = task, subtask = subtask)
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
					list_number_selected_str = str(list_number_selected)[1:-1] + "m"
					debug(list_number_selected_str = list_number_selected_str)

					return self.navigator(username, password, no_verify, use_all, force_https, force_http, proxy, minute_add, download_path, confirm, force_wget, list_number_selected_str, data, False, sort_by = sort_by)
										
			elif str(q).strip()[-1] == 'e':
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
				qr = raw_input(make_colors("Input Remote URL: ", 'lightwhite', 'blue'))
				if qr:
					if qr.strip() == 'c':
						qr = clipboard.paste()
					if 'http' in qr or 'ftp' in qr:
						self.remote_upload(str(qr))
			
			elif q == 'x' or q == 'q':
				task = make_colors("EXIT", 'lightwhite', 'lightred')
				subtask = make_colors("System Exit !", 'lightwhite', 'lightred') + " "
				bar.update(self.max_value, task = task, subtask = subtask)
				print("\n")
				sys.exit(make_colors("EXIT !", 'lightwhite', 'lightred'))
				#sys.exit()
			elif q == 'h' or q == '-h':
				help_str = """usage: 1fichier.py [-h] [-s SORT_BY] [-r REMOTE_UPLOAD] [-p DOWNLOAD_PATH]
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
		return self.navigator(username, password, no_verify, use_all, force_https, force_http, proxy, minute_add, download_path, confirm, force_wget, sort_by = sort_by)
	
	def print_nav(self):
		note1 = make_colors("Select Number", 'lightwhite', 'lightblue') + " [" + make_colors("[n]m = remove n", 'lightwhite', 'lightred') + ", " + make_colors("r = remote upload", "lightwhite", 'magenta') + ", " + make_colors("[n]e = Export n to file .csv", 'red', "lightyellow") + ", " + make_colors('h|-h = Print command help', 'black', 'lightgreen') + ", " +  make_colors("e[x]it|[q]uit = exit|quit", 'lightred') + ", " + make_colors("download_path=[dir], set download path", 'lightblue') + ", " + make_colors("[n = Number selected] default select number is download n", 'lightwhite', 'lightblue') + ": "
		
		q = raw_input(note1)
		return q		
		
	def build_dict(self, seq, key):
		data = dict((d[key], dict(d, index=index)) for (index, d) in enumerate(seq))
		debug(data = data)
		return data
		
	def download_link(self, id_rel):
		if not self.sess.cookies.get('SID'):
			self.login()
		url = self.url + 'console/link.pl'
		if id_rel:
			data = {
				'selected[]':id_rel,
			}
			a = self.sess.post(url, data=data)
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
			a = self.sess.post(url, data=data)
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
		a = self.sess.get(url)
		b = bs(a.content, 'lxml')
		data = []
		ru_item = b.find_all('div', {'id':re.compile('d')})
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
		a = self.sess.get(url)
		b = bs(a.content, 'lxml')
		data = []
		alc = b.find('div', {'class':'alc'})
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
				text = li.text
				debug(text = text)
				if text:
					if "Download failed" in text:
						return False
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
		a = self.sess.post(url, data=data)
		content = a.content
		debug(content = content)
		if 'Files removed' in content:
			return True
		else:
			return False
		
	def remote_upload(self, links):
		if not self.sess.cookies.get('SID'):
			self.login()
		
		self.max_value = 100
		self.clean_dones()
		url = self.url + 'console/remote.pl'
		for i in links:
			if i == 'c':
				i = clipboard.paste()
			data = {
				'links': i 
			}
			
			a = self.sess.post(url, data = data)
			content = a.content
			#print("content =", content)
			if "Can not find any valid link" in content:
				print(make_colors("Can not find any valid link !", 'lightwhite', 'lightred'))
				return False
			debug(content = content)
			check = re.findall('1 recorded links', content)
			if check:
				bar = progressbar.ProgressBar(max_value = self.max_value, prefix = self.prefix, variables = self.variables)
				task = make_colors("Action", "lightwhite", "blue")
				subtask = make_colors("RemoteUpload", "lightwhite", "magenta") + " "
				while 1:
					data_done = self.check_done()
					done = False
					if data_done:
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
					    })
		return proxy_list
	
	def usage(self):
		parser = argparse.ArgumentParser(formatter_class = argparse.RawTextHelpFormatter)
		parser.add_argument('-s', '--sort-by', action = 'store', help = 'Sortby: time/timestamp, date, name, rel, size')
		parser.add_argument('-r', '--remote-upload', action = 'store', help = 'Remote Upload')
		parser.add_argument('-p', '--download-path', action = 'store', help = 'Download Path or Export save path', default = os.getcwd())
		parser.add_argument('-d', '--download', action = 'store', help = 'Convert Link and download it')
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
				self.remote_upload(args.remote_upload)
			#else:
			print("\n")
			self.navigator(args.username, args.password, args.no_verify, args.all, args.https, args.http, proxy, download_path = args.download_path, confirm = args.confirm, force_wget = args.wget, sort_by = args.sort_by)
		
if __name__ == '__main__':
	c = onefichier()
	c.usage()
	#c.remove("C_0_g38aio8euw61hrvjvxw5")
	#c.get_download_link("https://1fichier.com/?13tkjkqtegzxu5ilewnl")
	#c.login()
	#c.list()
	#dl = c.download_link("C_0_13tkjkqtegzxu5ilewnl")
	#c.export("C_0_13tkjkqtegzxu5ilewnl")
	#c.remote_upload(sys.argv[1:])
	#c.check_done()
	#if dl:
	#	link = c.get_download_link(dl)
	#	debug(link = link)