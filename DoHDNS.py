from dnslib import *
import requests
import socket, ssl

import time

import pandas as pd

domains = ["gla.ac.uk",
          "nationalgeographic.co.uk",
          "facebook.com",
          "google.com",
          "kjhdfce.com",
          "kjhdfce.co.uk",
          "cbse.nic.in",
          "the_omnia.com",
          "penguin.com",
          "Aynrand.com"]
doh_resolver = {"Cloudflare":"https://cloudflare-dns.com/dns-query",
                "Google":"https://dns.google/dns-query",
                "Local":"https://mozilla.cloudflare-dns.com/dns-query",
                "OpenDNS":"https://doh.opendns.com/dns-query",
                "Quad9":"https://dns.quad9.net/dns-query",
                "Adguard":"https://dns.adguard.com/dns-query"}
dns_resolvers = {"Cloudflare":"1.0.0.1",
                "Google":"8.8.4.4",
                "Local":"109.246.13.15",
                "OpenDNS":"208.67.222.222",
                "Quad9":"9.9.9.9",
                "Adguard":"176.103.130.130"}

for domain in domains:
    print("Domain: ", domain)
    message = DNSRecord.question(domain)
    for resolver in doh_resolver:
        print("\nDoH Resolver: ", resolver)
        mode = 'doh'
        column_name = ["Time"]
        data = pd.DataFrame(columns = column_name)
        for i in range(100):
            try:
                print("Iteration: ", i+1)
                params = {'dns':base64.urlsafe_b64encode(message.pack()).replace(b"=",b"")}
                headers = {'scheme':'https',
                           'ct': 'application/dns-message',
                           'accept':'application/dns-message',
                           'cl':'33'
                          }
                start_time = time.time()
                answers = requests.get(doh_resolver[resolver], headers=headers, params=params)
                end_time = time.time()
                time_taken = end_time - start_time
                print("\nTime taken: ",time_taken)
                s = pd.Series([time_taken], index=["Time",])
                data = data.append(s, ignore_index=True)
            except:
                s = pd.Series([0], index = ["Time"])
                data = data.append(s, ignore_index=True)
        data.to_csv("{}+{}+{}.csv".format(domain, mode, resolver))

    for resolver in dns_resolvers:
        print("\nDNS Resolver: ", resolver)
        mode = 'dns'
        bytesToSend = message.pack()
        data = pd.DataFrame(columns = column_name)
        for i in range(100):
            print("Iteration: ", i+1)
            try:
                UDPsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                start_time = time.time()
                UDPsocket.sendto(bytesToSend, (dns_resolvers[resolver], 53))
                answers, server = UDPsocket.recvfrom(4096)
                end_time = time.time()
                UDPsocket.close()
                time_taken = end_time - start_time
                print("\nTime taken: ",time_taken)
                s = pd.Series([time_taken], index=["Time"])
                data = data.append(s, ignore_index=True)
            except:
                print("\nTime taken: 0")
                s = pd.Series([0], index = ["Time"])
                data = data.append(s, ignore_index=True)
        data.to_csv("CSVs/{}+{}+{}.csv".format(domain, mode, resolver))

