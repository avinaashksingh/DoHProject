import dns.resolver
from dns.query import udp
from dns.query import https
from dns.message import make_query

import argparse
import sys
import time

import pandas as pd

from openpyxl import Workbook, load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows

parser = argparse.ArgumentParser() # Initiate the parser
parser.add_argument("--domain", "-d", help="Input the requested domain.")
parser.add_argument("--filepath", "-f", help="Enetr the Microsoft excel file where the result has to be stored")

if len(sys.argv) < 2:
    parser.print_usage()
    sys.exit(1)

args = parser.parse_args()

Configurations = {"Cloudflare": {"ch":"doh", "resolver":"1.1.1.1"},
                  "Google": {"ch":"doh", "resolver":"8.8.8.8"},
                  "Baidu(China)": {"ch":"dns", "resolver":"180.76.76.76"},
                  "Shenzen(China)": {"ch":"dns", "resolver":"202.46.34.75"}}       
domain = args.domain

message = dns.message.make_query(domain, dns.rdatatype.NS)
#print("\nMessage: ", message)

entries = {}

for item in Configurations:

    if Configurations[item]["ch"] == 'dns':
        try:
	        start_time = time.time()
	        answers = udp(message, Configurations[item]["resolver"])
	        end_time = time.time()
	        entries[item] = {"Time": end_time - start_time, "Result": str(answers)}
        except:
	        entries[item] = {"Time": "----", "Result": "----"}

    if Configurations[item]["ch"] == "doh":
        try:
	        start_time = time.time()
	        answers = https(message, Configurations[item]["resolver"])
	        end_time = time.time()
	        entries[item] = {"Time": end_time - start_time, "Result": str(answers)}
        except:
	        entries[item] = {"Time": "$$$$", "Result": "$$$$"}

df = pd.DataFrame(entries)

if args.filepath:
    wb = load_workbook(args.filepath)
    if not wb[domain]:
        sheet1 = wb.create_sheet(domain,0)
    active = wb[domain]
    for x in dataframe_to_rows(df):
        active.append(x)
    wb.save(args.filepath)   
else:
    wb = Workbook()
    sheet1 = wb.create_sheet(domain,0)
    active = wb[domain]
    for x in dataframe_to_rows(df):
        active.append(x)
    wb.save("Entries.xlsx")





