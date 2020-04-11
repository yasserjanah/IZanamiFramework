#!/bin/bash

GREEN="\033[92m"
RED="\033[31m"
WHITE="\033[97m"
YELLOW="\033[33m"
BLUE="\033[34m"
CYAN="\033[36m"
BLINK="\033[6m"
BOLD="\033[1m"
RESET="\033[0m"

function check_port(){
if `sudo netstat -tulpn | grep "0.0.0.0:$1" > /dev/null` || `sudo netstat -tulpn | grep "127.0.0.1:$1" > /dev/null`;then
   port_is_in_use $1
   exit 1
else
   port_is_available $1
fi
}
function port_is_in_use(){ echo -e "\t${RED}** ${WHITE} port ${RED}${1}${WHITE} is in use.\n\t${RED}** ${WHITE} please ${RED}stop${WHITE} your local server ${RED}OR${WHITE} any application that using port ${RED}${1}${WHITE}\n" ; }

function port_is_available(){ 
   if [ $1 -eq 80 ]; then
      echo -e "\t${GREEN}** ${WHITE}Server running on http://0.0.0.0:${GREEN}${1}${WHITE}/"
   else
      echo -e "\t${GREEN}** ${WHITE}Server running on https://0.0.0.0:${GREEN}${1}${WHITE}/"
   fi
}

__banner__="${WHITE}\n\tWeb Server ${YELLOW}${BOLD}»»${RESET}${WHITE} part of${BLINK}${BOLD} I Z A N A M I${RESET}${WHITE} Framework ${YELLOW}${BOLD}»»${RESET}${WHITE} by ${BOLD}${CYAN}@${RED}YasserJanah${RESET} (${BOLD}${BLUE}fb/yasser.janah${RESET})\n"

echo -e ${__banner__}

if [[ $EUID -ne 0 ]]; then
   echo -e "${RED} run the script as root...${WHITE}\n try : ${GREEN}sudo${WHITE} ./runserver.sh\n" 
   exit 1
fi

check_port 80
check_port 443

echo " "

cd ./server/IZWebServer && ( gunicorn -b 0.0.0.0:80 -w 1 --reload IZWebServer.wsgi:application 2> /dev/null & ) ; gunicorn -b 0.0.0.0:443 -w 1 --reload IZWebServer.wsgi:application --certfile=certs/server.crt --keyfile=certs/server.key 2> /dev/null
