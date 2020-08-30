from dnslib import *
import requests
import socket, ssl

import time

import pandas as pd
domains = ["facebook.com",
           "Instagram.com",
           "tiktok.com",
           "twitter.com", 
           "Wechat.com",
           "https://www.bbc.co.uk/news",
           "https://www.telegraph.co.uk/news/",
           "https://www.thehindu.com",
           "https://www.dailymail.co.uk/news",
           "https://www.google.com/search?q=Covid-19",
           "https://www.google.com/search?q=Apple Sweatshops",
           "https://www.google.com/search?q=Mica Child Labour",
           "https://www.google.com/search?q=Garment Sweatshops",
           "https://www.google.com/search?q=Leather Pollution Kanpur",
           "Netflix.com",
           "primevideo.com",
           "tv.apple.com",
           "hulu.com",
           "udacity.com",
           "mooc.org",
           "udemy.com",
           "khanacademy.org",
           "https://aws.amazon.com/training/",
           "gla.ac.uk",
           "cornell.edu",
           "nyu.edu",
           "slu.edu",
           "penguin.com",
           "aynrand.com",
           "https://www.harpercollins.com",
           "expedia.com",
           "makemytrip.com",
           "airbnb.com",
           "shein.com",
           "amazon.com",
           "flipkart.com",
           "etsy.com",
           "minted.com",
           "cosmopolitan.com"]
resolvers = {"Cloudflare":{"mode":"doh", "ad":"https://cloudflare-dns.com/dns-query"},
             "Google":{"mode":"doh", "ad":"https://dns.google/dns-query"},
             "Islamabad":{"mode":"dns", "ad":"103.209.52.250"},
             "Rawalpindi":{"mode":"dns", "ad":"119.160.80.164"},
             "Karachi":{"mode":"dns", "ad":"58.27.149.70"}}

column_name = ["Domain", "Resolver", "Result"]
data = pd.DataFrame(columns = column_name)

for domain in domains:
    print("Domain: ", domain)
    message = DNSRecord.question(domain)
    for resolver in resolvers:
        print("Resolver: ", resolver)
        if resolvers[resolver]["mode"] == "dns":
            try:
                bytesToSend = message.pack()
                UDPsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                start_time = time.time()
                UDPsocket.sendto(bytesToSend, (resolvers[resolver]["ad"], 53))
                answers, server = UDPsocket.recvfrom(4096)
                end_time = time.time()
                print("Time taken: ", end_time-start_time)
                UDPsocket.close()
                s = pd.Series([domain, resolver, str(DNSRecord.parse(answers))], index = ["Domain", "Resolver", "Result"])
                data = data.append(s, ignore_index=True)
            except:
                s = pd.Series([domain, resolver, "----"], index = ["Domain", "Resolver", "Result"])
                data = data.append(s, ignore_index=True)
        if resolvers[resolver]["mode"] == "doh":
            try:
                params = {'dns':base64.urlsafe_b64encode(message.pack()).replace(b"=",b"")}
                headers = {'scheme':'https',
                           'ct': 'application/dns-message',
                           'accept':'application/dns-message',
                           'cl':'33'
                           }
                start_time = time.time()
                answers = requests.get(resolvers[resolver]["ad"], headers=headers, params=params)
                end_time = time.time()
                time_taken = end_time - start_time
                print("\nTime taken: ",time_taken)
                s = pd.Series([domain, resolver, str(DNSRecord.parse(answers.content))], index=["Domain", "Resolver", "Result"])
                data = data.append(s, ignore_index=True)
            except:
                s = pd.Series([domain, resolver, "----"], index = ["Domain", "Resolver", "Result"])
                data = data.append(s, ignore_index=True)

data.to_csv("India.csv")

