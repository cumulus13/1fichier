#!/usr/bin/env python

from __future__ import print_function
import os
import sys
import clipboard
import traceback
import bitmath
from datetime import datetime
from xnotify import notify
from pydebugger.debug import debug
from make_colors import make_colors
import re

if sys.version_info.major == 3:
    from urllib.parse import urlparse
else:
    from urlparse import urlparse

def logger(config, message, status="info"):
    logfile = os.path.join(os.path.dirname(__file__), os.path.basename(config.configname))
    if not os.path.isfile(logfile):
        lf = open(logfile, 'wb')
        lf.close()
    real_size = bitmath.getsize(logfile).kB.value
    max_size = config.get_config("LOG", 'max_size')
    debug(max_size = max_size)
    if max_size:
        debug(is_max_size = True)
        try:
            max_size = bitmath.parse_string_unsafe(max_size).kB.value
        except:
            max_size = 0
        if real_size > max_size:
            try:
                os.remove(logfile)
            except:
                print("ERROR: [remove logfile]:", traceback.format_exc())
            try:
                lf = open(logfile, 'wb')
                lf.close()
            except:
                print("ERROR: [renew logfile]:", traceback.format_exc())


    str_format = datetime.strftime(datetime.now(), "%Y/%m/%d %H:%M:%S.%f") + " - [{}] {}".format(status, message) + "\n"
    with open(logfile, 'ab') as ff:
        ff.write(str_format)

def downloader(url, config, download_path = None, saveas = None, confirm = False, ext = None, copyurl_only = False, nodownload = False):
    # os.environ.update({"DEBUG_SERVER":'1'})
    # os.environ.update({"DEBUGGER_SERVER":'50002'})
    download_path0 = download_path
    url_download = None
    saveas0 = saveas
    if ext:
        ext = ext.lower()
    debug(ext = ext)
    debug(download_path = download_path)
    debug(saveas = saveas)
    error = False
    season_from_name = ''
    if ext and ext[0] == ".":
        ext = ext[1:]
    try:
        if not os.path.isdir(download_path) and not copyurl_only:
            download_path = None
    except:
        pass
    if not download_path and not copyurl_only and not nodownload:
        if os.getenv('DOWNLOAD_PATH'):
            download_path = os.getenv('DOWNLOAD_PATH')
        if config.get_config('DOWNLOAD', 'path', os.getcwd()):
            download_path = config.get_config('DOWNLOAD', 'path')
            debug(download_path_config = download_path)
    debug(download_path0 = download_path)

    if not copyurl_only and not nodownload:
        print(make_colors("DOWNLOAD_PATH:", 'lw', 'bl') + " " + make_colors(download_path, 'b', 'ly'))
    # sys.exit()
    if not download_path and not copyurl_only and not nodownload:
        download_path = ''
    if 'linux' in sys.platform and download_path and not os.path.isdir(download_path) and not copyurl_only and not nodownload:

        debug(download_path0 = download_path)
        if not os.path.isdir(download_path):
            this_user = getpass.getuser()
            login_user = os.getlogin()
            env_user = os.getenv('USER')
            debug(login_user = login_user)
            debug(env_user = env_user)
            this_uid = os.getuid()
            download_path = r"/home/{0}/Downloads".format(login_user)
            debug(download_path = download_path)

    if download_path and not os.path.isdir(download_path) and not copyurl_only and not nodownload:
        try:
            os.makedirs(download_path)
        except:
            pass

    if download_path and not os.path.isdir(download_path) and not copyurl_only and not nodownload:
        try:
            os.makedirs(download_path)
        except OSError:
            tp, tr, vl = sys.exec_info()
            debug(ERROR_MSG = vl.__class__.__name__)
            if vl.__class__.__name__ == 'OSError':
                print(make_colors("Permission failed make dir:", 'lw', 'lr', ['blink']) + " " + make_colors(download_path, 'lr', 'lw'))


    if not download_path and not copyurl_only and not nodownload:
        download_path = os.getcwd()
    if download_path and not os.access(download_path, os.W_OK|os.R_OK|os.X_OK) and not copyurl_only:
        print(make_colors("You not have Permission save to dir:", 'lw', 'lr' + " " + make_colors(download_path, 'lr', 'lw')))
        download_path = os.getcwd()
    if not copyurl_only and not nodownload:
        print(make_colors("DOWNLOAD PATH:", 'lw', 'bl') + " " + make_colors(download_path, 'lw', 'lr'))
    debug(download_path = download_path)
    debug(url = url)
    # try:
    #     clipboard.copy(url)
    # except:
    #     pass
    try:
        from idm import IDMan
        d = IDMan()
    except:
        from pywget import wget as d
    name = None
    cookies = {}

    debug(copyurl_only = copyurl_only)

    debug(netloc = urlparse(url).netloc)

    if 'solidfiles' in urlparse(url).netloc:
        try:
            from solidfiles import Solidfiles
            url_download, url_stream, info = Solidfiles.get(url)[0]
        except:
            traceback.format_exc()
            error = True            

    elif 'dutrag' in urlparse(url).netloc or "unityplayer" in urlparse(url).netloc:
        try:
            from dutrag import Dutrag
            url_download, savename, savesize = Dutrag.generate(url)
            debug(url_download = url_download)
            debug(savename = savename)
            debug(savesize = savesize)
            if url_download:
                url_download = url_download.get('data')[0].get('file')
                debug(url_download = url_download)
        except:
            traceback.format_exc()
            error = True            

    elif "player.animesail" in urlparse(url).netloc:
        url = requests.get(url).url
        return downloader(url, download_path0, saveas0, confirm, ext, copyurl_only, nodownload)

    elif 'mega.nz' in urlparse(url).netloc:
        print(make_colors("URL to Generate:", 'lw', 'bl') + " " + make_colors(url, 'y'))
        debug(CONFIGFILE = config.filename())
        from mega import Mega
        mm = Mega()
        mega_username = config.get_config('mega.nz', 'username')
        debug(mega_username = mega_username)
        mega_password = config.get_config('mega.nz', 'password')
        debug(mega_password = mega_password)

        m = mm.login(mega_username, mega_password)
        url_download = m.get_download_url(url)
        debug(url_download = url_download)


    elif 'files.im' in urlparse(url).netloc:
        try:
            from filesim import Filesim
            debug(url = url)
            url_download = Filesim.generate(url)
            debug(url_download = url_download)
        except:
            traceback.format_exc()
            error = True

    elif 'justpaste' in urlparse(url).netloc:
        try:
            from justpaste import Justpaste
            url_download = Justpaste.navigator(url)
            if url_download:
                return downloader(url_download, download_path0, saveas, confirm, ext)

        except:
            traceback.format_exc()
            error = True

    elif 'racaty' in urlparse(url).netloc:
        try:
            from racaty import racaty
            url_download = racaty(url)
            debug(url_download = url_download)
        except:
            print("ERROR:", traceback.format_exc())
            error = True

    elif urlparse(url).netloc == "drive.google.com":
        if urlparse(url).query:
            if "id=" == urlparse(url).query[:3]:
                url_download = url
            else:
                error = True

    elif 'uptobox' in urlparse(url).netloc:
        try:
            from uptobox import Uptobox
            url_download = Uptobox.get_download_link(url)
            print(make_colors("DOWNLOAD URL (uptobox) :", 'b', 'g')  + " " + make_colors(url_download, 'b', 'g'))
        except:
            traceback.format_exc()
            error = True

    elif 'mir.cr' in urlparse(url).netloc or 'mirrored' in urlparse(url).netloc:
        try:
            from mirrored import Mirrored
            url_download = Mirrored.navigator(url)
            debug(url_download = url_download)
            return downloader(url_download, download_path0, saveas0, confirm, ext)
        except:
            traceback.format_exc()
            error = True

    elif 'clicknupload' in urlparse(url).netloc:
        try:
            from clicknupload import Clicknupload
            url_download = Clicknupload.main(url)
            debug(url_download = url_download)
            # return downloader(url_download, download_path0, saveas0, confirm, ext)
        except:
            traceback.format_exc()
            error = True

    elif 'zippyshare' in urlparse(url).netloc:
        try:
            from zippyshare_generator import zippyshare
            z = zippyshare.zippyshare()
            url_download, name, cookies = z.generate(url)
            print(make_colors("URL (zippyshare):", 'lw', 'bl') + " " + make_colors(str(url_download), 'lw', 'r'))
        except:
            print("TRACEBACK:", traceback.format_exc())
            error = True
        print(make_colors("NAME (zippyshare):", 'lw', 'bl') + " " + make_colors(str(name), 'lw', 'm'))

    elif 'anonfile' in urlparse(url).netloc:
        try:
            from anonfile import Anonfile
            a = Anonfile()
            url_download = a.generate(url)
            debug(url_download = url_download)
            if not url_download:
                error = True
        except:
            traceback.format_exc()
            error = True

    elif 'mediafire' in urlparse(url).netloc:
        try:
            from mediafire import mediafire
            a = mediafire.Mediafire()
            url_download = a.generate(url)
            debug(url_download = url_download)
        except:
            traceback.format_exc()
            error = True

    debug(error = error)

    if error:
        logger(config, "downloader: error: {}".format(url), "error")
        try:
            clipboard.copy(url)
            logger(config, "downloader: error: {} --> clipboard".format(url), "error")
        except:
            pass
        print(make_colors("[ERROR] Get download link", 'lw', 'r') + ", " + make_colors("copy URL to clipboard", 'y'))
    else:
        debug(copyurl_only = copyurl_only)

        if copyurl_only:
            if url_download:
                print(make_colors("Url Download:", 'lw', 'lr') + " " + make_colors(url_download, 'y'))
                clipboard.copy(url_download)
                logger(config, "downloader: {} --> clipboard".format(url_download), "debug")
                return url_download
            else:
                print(make_colors("URL:", 'lw', 'lr') + " " + make_colors(url, 'y'))
                clipboard.copy(url)
                logger(config, "downloader: {} --> clipboard".format(url), "notice")
                return url
        if not saveas and name:
            saveas = name
        if not ext and name:
            try:
                if len(os.path.splitext(name)) > 1:
                    ext = os.path.splitext(name)[1]
                    if saveas:
                        saveas = saveas + ext
                        debug(saveas = saveas)
            except:
                pass
        debug(url_download = url_download)
        if not url_download:
            clipboard.copy(url)
            return url
        if not ext and not name:
            debug(url_download = url_download)
            debug(split_url_download = os.path.split(url_download))
            debug(split_ext = os.path.splitext(os.path.split(url_download)[-1]))
            ext = os.path.splitext(os.path.split(url_download)[-1])[1]#.lower()
            debug(ext = ext)
            if ext in [".mp4", ".mkv", ".avi"]:
                name = os.path.split(url_download)[-1]
        if not ext or ext.strip() == '':
            ext = "mp4"
        if ext and saveas:
            if not os.path.splitext(saveas)[1].lower() in [".mp4", ".mkv", ".avi"]:
                saveas = saveas + "." + str(ext).lower()
        debug(ext = ext)
        debug(saveas = saveas)
        if nodownload:
            if url_download:
                return url_download, saveas
            else:
                return '', ''
        print(make_colors("SAVEAS:", 'lw', 'bl') + " " + make_colors(saveas, 'lw', 'r'))
        debug(url_download = url_download)
        debug(download_path = download_path)
        if saveas:
            while 1:
                if saveas[-1] == ".":
                    saveas = saveas[:-1]
                else:
                    break
        if sys.platform == 'win32':
            logger(config, "downloader [win32]: downloading: {} --> {} --> {}".format(url, url_download, saveas))
            d.download(url_download, download_path, saveas, confirm = confirm)
            logger(config, "downloader [win32]: finish: {} --> {} --> {}".format(url, url_download, saveas))

        else:
            logger(config, "downloader [linux]: downloading: {} --> {} --> {}".format(url, url_download, saveas))
            download_linux(url_download, config, download_path, saveas, cookies)
            logger(config, "downloader [linux]: finish: {} --> {} --> {}".format(url, url_download, saveas))

    icon = None
    if os.path.isfile(os.path.join(os.path.dirname(__file__), 'logo.png')):
        icon = os.path.join(os.path.dirname(__file__), 'logo.png')

    if sys.platform == 'win32':
        notify("Download start: ", saveas, "Neonime", "downloading", icon = icon)    
    else:
        notify("Download finish: ", saveas, "Neonime", "finish", icon = icon)

    if url_download:
        return url_download, ''
    return url, ''

def download_linux(url, config, download_path=os.getcwd(), saveas=None, cookies = {}, downloader = 'wget'):
    '''
        downloader: aria2c, wget, uget, persepolis
    '''
    if not download_path or not os.path.isdir(download_path):
        if config.get_config('DOWNLOAD', 'path', os.getcwd()):
            download_path = config.get_config('DOWNLOAD', 'path')
    print(make_colors("DOWNLOAD_PATH (linux):", 'lw', 'bl') + " " + make_colors(download_path, 'b', 'ly'))
    aria2c = os.popen3("aria2c")
    wget = os.popen3("wget")
    persepolis = os.popen3("persepolis --help")

    if downloader == 'aria2c' and not re.findall("not found\n", aria2c[2].readlines()[0]):
        if saveas:
            saveas = '-o "{0}"'.format(saveas.encode('utf-8', errors = 'ignore'))
        os.system('aria2c -c -d "{0}" "{1}" {2} --file-allocation=none'.format(os.path.abspath(download_path), url, saveas))
    elif downloader == 'wget' and not re.findall("not found\n", wget[2].readlines()[0]):
        filename = ''
        if saveas:
            filename = os.path.join(os.path.abspath(download_path), saveas.decode('utf-8', errors = 'ignore')) 
            saveas = ' -O "{}"'.format(os.path.join(os.path.abspath(download_path), saveas.decode('utf-8', errors = 'ignore')))
        else:
            saveas = '-P "{0}"'.format(os.path.abspath(download_path))
            filename = os.path.join(os.path.abspath(download_path), os.path.basename(url))
        headers = ''
        header = ""
        if cookies:
            for i in cookies: header +=str(i) + "= " + cookies.get(i) + "; "
            headers = ' --header="Cookie: ' + header[:-2] + '"'
        cmd = 'wget -c "{}" {}'.format(url, saveas) + headers
        print(make_colors("CMD:", 'lw', 'lr') + " " + make_colors(cmd, 'lw', 'r'))
        os.system(cmd)
        if config.get_config('policy', 'size'):
            size = ''
            try:
                size = bitmath.parse_string_unsafe(config.get_config('policy', 'size'))
            except ValueError:
                pass
            if size and not bitmath.getsize(filename).MB.value > size.value:
                print(make_colors("REMOVE FILE", 'lw', 'r') + " [" + make_colors(bitmath.getsize(filename).kB) + "]: " + make_colors(filename, 'y') + " ...")
                os.remove(filename)

    elif downloader == 'persepolis'  and not re.findall("not found\n", persepolis[2].readlines()[0]):
        os.system('persepolis --link "{0}"'.format(url))
    else:
        try:
            from pywget import wget as d
            d.download(url, download_path, saveas.decode('utf-8', errors = 'ignore'))
        except:
            print(make_colors("Can't Download this file !, no Downloader supported !", 'lw', 'lr', ['blink']))
            clipboard.copy(url)

    