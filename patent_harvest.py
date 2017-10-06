#!/usr/bin/env python
import sys, os, time, random
import re, pickle, argparse, fileinput, requests

parser = argparse.ArgumentParser(description='downloads patents within a number range')
parser.add_argument('--start', dest='pn_start', type=int, 
                    default=7640598, help='starting value for patent number range')
parser.add_argument('--end', dest='pn_end', type=int, 
                    default=8087093, help='ending value for patent number range')

api_endpoint = 'http://patft.uspto.gov/netacgi/nph-Parser'

def main(args):
    for i, patnum in enumerate(range(args.pn_start,args.pn_end+1)):
        patpath = patent_path(patnum)
        status = download_patent(patnum,patpath)                
        print '{}/{} {} ({})'.format(i, args.pn_end - args.pn_start, patnum, status)
    
def download_patent(patent_number,patent_path):
    if os.path.exists(patent_path):
        return 'Exists'
    
    api_params = {'Sect1': 'PTO1',
            'Sect2': 'HITOFF',
            'd': 'PALL',
            'p': 1,
            'u': '/netahtml/TO/srchnum.htm',
            'r': 1,
            'f': 'G',
            'l': 50,
            's1': '{}.PN.'.format(patent_number) }
    
    try:
        response = get_request(api_endpoint,api_params)
    except:
        time.sleep(30)
        return 'Connection failed'
    
    if response is None:
        return 'Skipped'
    elif len(response) <= 5000:
        time.sleep(3)
        return 'Bad Response'
    else:
        rootdir = os.path.join(*patent_path.split('/')[:-1])
        if not os.path.exists(rootdir):
            os.makedirs(rootdir)
        
        with open(patent_path, 'w') as f:
            print >> f, response
            time.sleep(1)
        
        return 'Success'
    
def get_request(url,params):
    r = requests.get(url, params)
    
    if r.status_code == 200:
        return r.text
    else:
        print >> sys.stderr, 'Error: http response {}'.format(r.status_code)
        return None

def patent_path(patent_number):
    patent_root = str(int(patent_number / 1000))
    return os.path.join('patents', patent_root, '{}.html'.format(patent_number))

if __name__ == '__main__':
    main(parser.parse_args())
