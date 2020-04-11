#!/bin/bash

GREEN="\033[92m"
RED="\033[31m"
BLUE="\033[34m"
BLINK="\033[5m"
RESET_BLINK="\033[25m"
WHITE="\033[97m"
if [[ $EUID -ne 0 ]]; then
   echo "${RED} ${1} must be run as root...${WHITE}" 
   exit 1
fi

function print_status(){ echo -e "${WHITE}[${BLUE}+${WHITE}] ${1}"; }

function print_success(){ echo -e "${WHITE}[${GREEN}+${WHITE}] ${1}"; }

function print_fail(){ echo -e "${WHITE}[${RED}+${WHITE}] ${1}"; }

function print_slowly(){ echo -ne "${WHITE}[${BLUE}+${WHITE}] " && for (( i=0; i<${#1}; i++ )); do echo -ne "${1:$i:1}"; sleep ${2}; done; echo;}

function check_cmd(){ command -v ${1} >/dev/null 2>&1 && return 0 || return 1;}

function install_python_for_debian_based(){ apt install python3 python3-dev libpython-dev python3-pip;}

function install_libnetfilter(){ apt install libnetfilter-queue -y; }

function install_net_tools(){ apt install net-tools; }

function install_missing_deps(){ pip3 install -r ../requirements.txt;}

current_time="$(date)"
print_slowly "Started at ${current_time}" 0.1

check_cmd "python3"
if [ $? -eq 0 ];then
	print_success "${WHITE}'${GREEN}python3${WHITE}' is installed..."
else
	print_fail "${WHITE}'${RED}python3${WHITE}' is not installed..."
	print_status "installing ${GREEN}${BLINK}python3${RESET_BLINK}${WHITE}..." && sleep 1.5 && install_python_for_debian_based
fi

check_cmd "pip3"
if [ $? -eq 0 ];then
	print_success "${WHITE}'${GREEN}pip3${WHITE}' is installed..."
else
	print_fail "${WHITE}'${RED}pip3${WHITE}' is not installed..."
	print_status "installing ${GREEN}${BLINK}pip3${RESET_BLINK}${WHITE}..." && sleep 1.5 && apt-get install python3-pip
fi

check_cmd "git"
if [ $? -eq 0 ];then
	print_success "${WHITE}'${GREEN}git${WHITE}' is installed..."
else
	print_fail "${WHITE}'${RED}git${WHITE}' is not installed..."
	print_status "installing ${GREEN}${BLINK}git${RESET_BLINK}${WHITE}..." && sleep 1.5 && apt-get install git
fi

check_cmd "nmap"
if [ $? -eq 0 ];then
	print_success "${WHITE}'${GREEN}nmap${WHITE}' is installed..."
else
	print_fail "${WHITE}'${RED}nmap${WHITE}' is not installed..."
	print_status "installing ${GREEN}${BLINK}nmap${RESET_BLINK}${WHITE}..." && sleep 1.5 && apt-get install nmap
fi

check_cmd "ifconfig"
if [ $? -eq 0 ];then
	print_success "${WHITE}'${GREEN}ifconfig${WHITE}' is installed..."
else
	print_fail "${WHITE}'${RED}python3${WHITE}' is not installed..."
	print_status "installing ${GREEN}${BLINK}ifconfig${RESET_BLINK}${WHITE}..." && sleep 1 && install_net_tools
fi

print_status "${WHITE}installing python3 libs from '${GREEN}requirements.txt${WHITE}'"
install_missing_deps
install_libnetfilter
