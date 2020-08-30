from dnslib import *
import requests
import socket, ssl

import argparse
import sys
import time

import pandas as pd


parser = argparse.ArgumentParser() # Initiate the parser
parser.add_argument("--domain", "-d", help="Input the requested domain.")

if len(sys.argv) < 2:
    parser.print_usage()
    sys.exit(1)

args = parser.parse_args()

#Various Resolver Configurations
Configurations = {"Cloudflare DOH": {"mode":"doh", "resolver":"https://cloudflare-dns.com/dns-query"},
                  "Mozilla Cloudflare": {"mode":"doh", "resolver":"https://mozilla.cloudflare-dns.com/dns-query"},
                  "Google DOH": {"mode":"doh", "resolver":"https://dns.google/dns-query"},
                  "Quad9": {"mode":"doh", "resolver":"https://dns.quad9.net/dns-query"},
                  "Comcast": {"mode":"doh", "resolver":"https://doh.xfinity.com/dns-query"},
                  "Adguard": {"mode":"doh", "resolver":"https://dns.adguard.com/dns-query"},
                  "Local": {"mode":"dns", "resolver":"109.246.13.15"},
                  "Cloudflare DNS": {"mode":"dns", "resolver":"1.1.1.1"},
                  "OpenDNS": {"mode":"dns", "resolver":"208.67.222.222"},
                  "Vodafone Idea India": {"mode":"dns", "resolver":"182.19.95.34"},
                  "Baidu(China)": {"mode":"dns", "resolver":"180.76.76.76"},
                  "Google DNS": {"mode":"dns", "resolver":"8.8.4.4"}}       
domain = args.domain
#Create the DNS message
message = DNSRecord.question(domain)
data = pd.read_csv("Entries.csv", usecols = ["Server", "Domain", "Time", "Result"])
#Make Queries
for item in Configurations:

    if Configurations[item]["mode"] == 'dns':
        try:
	        #Enter code here to send the request message using UDP socket and get a reply back 
            bytesToSend = message.pack()
            UDPsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            start_time = time.time()
            UDPsocket.sendto(bytesToSend, (Configurations[item]["resolver"], 53))
            answers, server = UDPsocket.recvfrom(4096)
            end_time = time.time()
            UDPsocket.close()
            s = pd.Series([item, domain, end_time - start_time, str(DNSRecord.parse(answers))], index = ["Server", "Domain", "Time", "Result"])
            data = data.append(s, ignore_index=True)
        except:
            s = pd.Series(["----", "----", "----", "----"], index = ["Server", "Domain", "Time", "Result"])
            data = data.append(s, ignore_index=True)

    if Configurations[item]["mode"] == "doh":
        try:
            params = {'dns':base64.urlsafe_b64encode(message.pack()).replace(b"=",b"")}
            headers = {'scheme':'https',
                   'ct': 'application/dns-message',
                   'accept':'application/dns-message',
                   'cl':'33'
                   }
            start_time = time.time()
            answers = requests.get(Configurations[item]["resolver"],headers=headers,params=params)
            end_time = time.time()
            s = pd.Series([item, domain, end_time - start_time, str(DNSRecord.parse(answers.content))], index = ["Server", "Domain", "Time", "Result"])
            data = data.append(s, ignore_index=True)
        except:
            s = pd.Series(["$$$$", "$$$$", "$$$$", "$$$$"], index = ["Server", "Domain", "Time", "Result"])
            data = data.append(s, ignore_index=True)
            
data.to_csv("Entries.csv")





