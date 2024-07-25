# Example usage: site_response.py -f <filename> -u <url> -t <timeout> -r <retries>
# Description: This script will check the response of a website (or websites) and return the status code.

import requests
import sys
import os
import threading
import ipaddress
import json

batch_size = 100 # number of threads to run at once
threads = [] # batches of 16 threads
urls = [] # urls to check per thread batch
returns = [] # status codes from threads (based n ID)

USAGE = 'Usage: site_response.py -f <filename> | -u <url> | -ip <ip range> [-t <timeout> -r <retries> -b <batch size>]'

def error(msg = None):
    if msg is not None:
        print(f'Error::{msg}')
    print(USAGE)
    sys.exit(1)

def check_response(url, timeout, retries, id=None):
    status_code = None
    for i in range(retries):
        try:
            response = requests.get(url, timeout=timeout)
            status_code = response.status_code
            break
        except requests.exceptions.RequestException as e:
            # print(f'Error::{e}')
            pass

    if id is not None:
        global returns
        returns[id] = str(status_code)
    
    if status_code is None:
        status_code = 'Error'

    return status_code

def parse_ip_range(ip_range):
    # return list of IPs with port 80 and 443 appended to the end
    ip_list = []
    try:
        ip_network = ipaddress.ip_network(ip_range)
    except ValueError as e:
        error(e)
        sys.exit(1)
    for ip in ip_network.hosts():
        ip_list.append(str(ip))
    return ip_list
    
def main():
    filename = None
    URL = None
    ip_range = None
    timeout = 1
    retries = 1
    multithreaded = False
    args = sys.argv[1:]

    if '-h' in args:
        error()
        sys.exit(1)

    if '-f' in args and '-u' in args:
        error('Please provide only one of either filename or URL')

    if '-f' in args:
        filename = args[args.index('-f') + 1]
    elif '-u' in args:
        url = args[args.index('-u') + 1]
    elif '-ip' in args:
        ip_range = args[args.index('-ip') + 1]
    else:
        error('Please provide a filename or URL')
    if '-t' in args:
        timeout = args[args.index('-t') + 1]
    if '-r' in args:
        retries = args[args.index('-r') + 1]
    if '-b' in args or '--batch' in args:
        global batch_size
        global threads
        global urls
        global returns
        multithreaded = True
        # check batch size is specified by user
        if '-b' in args:
            batch_size = args[args.index('-b') + 1]
        elif '--batch' in args:
            batch_size = args[args.index('--batch') + 1]
        try:
            batch_size = int(batch_size)
        except ValueError as e:
            error(e)
        if batch_size < 1:
            error('Batch size must be greater than 0')

    # verify arg types
    if filename :
        if not isinstance(filename, str):
            error('Filename must be a string')
        if os.path.exists(filename) is False:
            error('File does not exist')
    if URL and not isinstance(url, str):
        error('URL must be a string')
    if not isinstance(timeout, int):
        error('Timeout must be an integer')
    if not isinstance(retries, int):
        error('Retries must be an integer')

    print(f'{'='*80}')
    print(f'Checking response(s) for {filename or URL} with timeout {timeout} and retries {retries}')
    print(f'{'='*80}')

    sites = {} # site: status code
    
    if filename:
        with open(filename) as f:
            print("First 5 lines in file")
            total_sites = sum(1 for line in f)
            f.seek(0)
            print(f'Total sites to check: {total_sites}')
            if multithreaded:
                for i, line in enumerate(f):
                    urls.append(line.strip())
                    if len(urls) == batch_size:
                        for i, url in enumerate(urls):
                            returns.append(None)
                            t = threading.Thread(target=check_response, args=(url, timeout, retries, i))
                            threads.append(t)
                            t.start()
                        for t in threads:
                            t.join()
                        for i, url in enumerate(urls):
                            sites[url] = returns[i]
                        urls = []
                        threads = []
                        returns = []
                    # print progress and flush stdout to show progress
                    print(f'{len(sites)}/{total_sites} sites requested', end='\r')
                    sys.stdout.flush()
                if len(urls) > 0:
                    for i, url in enumerate(urls):
                        returns.append(None)
                        t = threading.Thread(target=check_response, args=(url, timeout, retries, i))
                        threads.append(t)
                        t.start()
                    for t in threads:
                        t.join()
                    for i, url in enumerate(urls):
                        sites[url] = returns[i]
                print(f'{len(sites)}/{total_sites} sites requested', end='\r')
                sys.stdout.flush()

            else:
                for line in f:
                    url = line.strip()
                    sites[url] = check_response(url, timeout, retries)
                    print(f'{len(sites)}/{total_sites} sites requested', end='\r')
                    sys.stdout.flush()
    elif URL:
        sites[URL] = check_response(URL, timeout, retries)
    elif ip_range:
        ip_list = parse_ip_range(ip_range)
        # add http and https to each IP
        ip_list = [f'http://{ip}' for ip in ip_list]
        # ip_list.extend([f'https://{ip}' for ip in ip_list])
        print('IP List Compiled')
        if multithreaded:
            ip_total = len(ip_list)
            processed = 0
            for ip in ip_list:
                urls.append(ip)
                if len(urls) == batch_size:
                    for i, url in enumerate(urls):
                        returns.append(None)
                        t = threading.Thread(target=check_response, args=(url, timeout, retries, i))
                        threads.append(t)
                        t.start()
                    for t in threads:
                        t.join()
                    for i, url in enumerate(urls):
                        sites[url] = returns[i]
                    urls = []
                    threads = []
                    returns = []
                
                print(f'{processed}/{ip_total} sites requested', end='\r')
                sys.stdout.flush()
                processed += 1
            if len(urls) > 0:
                for i, url in enumerate(urls):
                    returns.append(None)
                    t = threading.Thread(target=check_response, args=(url, timeout, retries, i))
                    threads.append(t)
                    t.start()
                for t in threads:
                    t.join()
                for i, url in enumerate(urls):
                    sites[url] = returns[i]
            print(f'{processed}/{ip_total} sites requested', end='\r')
            sys.stdout.flush()
        else:
            for ip in ip_list:
                sites[ip] = check_response(ip, timeout, retries)
                print(f'{len(sites)}/{len(ip_list)} sites requested', end='\r')
                sys.stdout.flush()

    else:
        error('Please provide a filename or URL')

    if URL:
        print(f'{"Site":<80} Status Code')
        print(f'{"-"*80}')
        if sites[URL] is None:
            print(f'{URL:<80}: Error')
        else:
            print(f'{URL:<80}: {sites[URL]}')
        exit(0)

    # create list of sites and status code is they key, so [404] = [site1, site2]
    site_code_lookup = {}
    for site, code in sites.items():
        if code in site_code_lookup:
            site_code_lookup[code].append(site)
        else:
            site_code_lookup[code] = [site]
    
    # dump site_code_lookup to json
    with open('site_code_lookup.json', 'w') as f:
        json.dump(site_code_lookup, f, indent=4)

    print()
    if not len(sites) > 100:
        print(f'{"Site":<80} Status Code')
        print(f'{"-"*80}')
        for site, status_code in sites.items():
            if status_code is None:
                print(f'{site:<80}: Error')
            else:
                print(f'{site:<80}: {status_code:<5}')
    print(f'{"="*80}')
    print("Final Report")
    print()
    
    print(f'{len(sites)} sites checked')
    # for each status code, print the number of sites that returned that code
    for code, sites in site_code_lookup.items():
        print(f'{len(sites)} sites returned status code {code}')

    print(f'{"="*80}')

    # ask user if they want to print out the sites that returned a specific status code by entering the code
    while True:
        code = input('Enter a status code to see the sites that returned that code (or q to quit): ')
        if code == 'q':
            break
        if code not in site_code_lookup:
            print('No sites returned that status code')
        else:
            print(f'Sites that returned status code {code}:')
            for site in site_code_lookup[code]:
                print(site)

if __name__ == '__main__':
    main()