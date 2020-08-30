from dnslib import *
import requests
import socket, ssl

import argparse
import sys
import time

import pandas as pd

parser = argparse.ArgumentParser() # Initiate the parser
parser.add_argument("--domain", "-d", help="Input the requested domain.")
parser.add_argument("--resolver", "-r", help="Input the resolver: URI for DoH, I.P for DNS.")
parser.add_argument("--name", "-n", help="Input the name of the resolver for data recording purposes")
parser.add_argument("--mode", "-m", help="Input the mode: doh for DoH, dns for DNS.")

if len(sys.argv) < 2:
    parser.print_usage()
    sys.exit(1)

args = parser.parse_args()
domain = args.domain
mode = args.mode
resolver = args.resolver
resolver_name = args.name

message = DNSRecord.question(domain)
column_name = ["Time", "Result"]
data = pd.DataFrame(columns = column_name)

if mode == 'dns':
    try:
        bytesToSend = message.pack()
        UDPsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        start_time = time.time()
        UDPsocket.sendto(bytesToSend, (resolver, 53))
        answers, server = UDPsocket.recvfrom(4096)
        end_time = time.time()
        UDPsocket.close()
        time_taken = end_time - start_time
        print("\nTime taken: ",time_taken)
        s = pd.Series([time_taken, str(DNSRecord.parse(answers))], index=["Time", "Result"])
        data = data.append(s, ignore_index=True)
    except:
        s = pd.Series([0, " "], index = ["Time", "Result"])
        data = data.append(s, ignore_index=True)

if mode == "doh":
    try:
        params = {'dns':base64.urlsafe_b64encode(message.pack()).replace(b"=",b"")}
        headers = {'scheme':'https',
                   'ct': 'application/dns-message',
                   'accept':'application/dns-message',
                   'cl':'33'
                   }
        start_time = time.time()
        answers = requests.get(resolver, headers=headers, params=params)
        end_time = time.time()
        time_taken = end_time - start_time
        print("\nTime taken: ",time_taken)
        s = pd.Series([time_taken, str(DNSRecord.parse(answers.content))], index=["Time", "Result"])
        data = data.append(s, ignore_index=True)
    except:
        s = pd.Series([0, " "], index = ["Time", "Result"])
        data = data.append(s, ignore_index=True)

data.to_csv("{}+{}+{}+censor.csv".format(domain, mode, resolver_name))
