import re
import os
import json
import socket
import requests
import argparse
import dns.resolver

def get_file(filename):
    if os.path.exists(filename):
        return filename
    return None

def check_ipv4(ip):
    pattern = "\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}"
    if re.fullmatch(pattern, ip):
        return True
    return False

def dns_port_open(ip):
    socket.setdefaulttimeout(1)
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if sock.connect_ex((ip, 53)) == 0:
            return True
        return False
    except:
        return False

def generate_resolvers():
    try:
        resp = requests.get("https://public-dns.info/nameservers.txt").text.split()
        resolvers = []
        for r in resp:
            if check_ipv4(r) and dns_port_open(r):
                print(f"{r}")
                resolvers.append(r)
        print("Fetched the list of resolvers.")
        return resolvers
    except requests.ConnectionError:
        print("ERROR: Facing connection issues")
        return None
    except requests.Timeout:
        print("ERROR: Connection timed out while making request.")
        return None

def find_tlds(target, resolverfile, wordlists):
    with open(resolverfile, "r") as rf:
        try:
            resolvers = json.loads(rf.read())["resolvers"]
        except:
            print("Invalid resolver file.")
            return None
    if resolvers == None:
        print("Could not get resolvers.")
        return None
    else:
        with open(wordlists, "r") as rf:
            tlds = rf.read().split()
        doms = []
        for tld in tlds:
            try:
                r = dns.resolver.Resolver(configure=False)
                r.nameservers = resolvers
                res = r.resolve(f"{target}{tld}")
                doms.append(f"{target}{tld}")
                print(f"{target}{tld}")
            except:
                pass
        return doms

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="TLD brute force script created by @n3hal_")
    parser.add_argument("-r", "--resolver", type=str, help="specify a file with a list of resolvers in JSON format.")
    parser.add_argument("-w", "--wordlist", type=str, help="specify a wordlist containing a list of tlds.")
    parser.add_argument("-o", "--output", type=str, help="save the output in a file.")
    parser.add_argument("-q", "--quiet", action="store_true", help="do not show the banner.")

    grp = parser.add_mutually_exclusive_group()
    grp.add_argument('-t', '--target', type=str, help="give a target for TLD brute force.")
    grp.add_argument('-g', '--generate', action="store_true", help="generate fresh public resolvers")

    args = parser.parse_args()

    if not args.quiet:
        print("""
 _____ __    ____  _____         _       
|_   _|  |  |    \| __  |___ _ _| |_ ___ 
  | | |  |__|  |  | __ -|  _| | |  _| -_|
  |_| |_____|____/|_____|_| |___|_| |___|

      Coded By: Nehal Zaman (@n3hal_)
    """)

    target = args.target
    generate = args.generate
    output_file = args.output
    if args.resolver:
        if get_file(args.resolver) != None:
            resolver_file = args.resolver
        else:
            resolver_file = "resolver.json"
    else:
            resolver_file = "resolver.json"

    if args.wordlist:
        if get_file(args.wordlist) != None:
            wordlist_file = args.wordlist
        else:
            wordlist_file = "tlds.txt"
    else:
        wordlist_file = "tlds.txt"

    if generate:
        res = generate_resolvers()
        if res != None:
            with open("resolver.json", "w") as wf:
                wf.write(json.dumps({"resolvers": res}))
    
    elif target:
        tlds = find_tlds(target.lower(), resolver_file, wordlist_file)
        if tlds == None:
            print("Could not get tlds.")
        else:
            if output_file:
                with open(output_file, "w") as wf:
                    for tld in tlds:
                        wf.write(tld + "\n")