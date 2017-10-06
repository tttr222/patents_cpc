#!/usr/bin/env python
import sys, os, time, random
import re, pickle, argparse, fileinput, json
from lxml import html

parser = argparse.ArgumentParser(description='parses downloaded patents within a number range')
parser.add_argument('--start', dest='pn_start', type=int, 
                    default=7640598, help='starting value for patent number range')
parser.add_argument('--end', dest='pn_end', type=int, 
                    default=8087093, help='ending value for patent number range')
parser.add_argument('--outfile', dest='outfile', type=str,
                    default='parsed.jsonl', help='file to output parsed dataset')

def main(args):
    parsed = []
    for i, patnum in enumerate(range(args.pn_start,args.pn_end+1)):
        patpath = patent_path(patnum)
        if not os.path.exists(patpath):
            status = 'No file'
        else:
            obj = parse_patent(patpath)
            if obj is None:
                status = 'Full-text not available'
            else:
                obj['patent_number'] = patnum
                parsed.append(obj)
                status = 'Parsed'
        
        print '{}/{} {} ({})'.format(i, args.pn_end - args.pn_start, patnum, status) 
    
    json_file = args.outfile
    with open(json_file,'w') as f:
        for obj in parsed:
            line = json.dumps(obj, sort_keys=True)
            f.write(line + '\n')
    
    print "Saved {} instances to {}".format(len(parsed), json_file)

def parse_patent(patent_path):
    with open(patent_path, "rb") as f:
        document_text = f.read()
        
    if "Full text is not available for this patent" in document_text:
        return None
    
    triggers = [{'keyword': 'United States Patent', 
                        'obj_key': 'date', 
                        'parse_func': parse_date,
                        'separate_header': False }, 
                       { 'keyword': 'Current CPC Class',
                        'obj_key': 'cpc_labels',
                        'parse_func': parse_class,
                        'separate_header': False },
                       { 'keyword': 'Abstract',
                        'obj_key': 'title',
                        'parse_func': parse_title,
                        'separate_header': False },
                       { 'keyword': 'Abstract',
                        'obj_key': 'abstract',
                        'parse_func': parse_abstract,
                        'separate_header': False },
                       { 'keyword': 'Claims',
                        'obj_key': 'claims',
                        'parse_func': parse_claims,
                        'separate_header': True },
                       { 'keyword': 'Description',
                        'obj_key': 'description',
                        'parse_func': parse_description,
                        'separate_header': True }]
    
    # This step is mostly to fix any broken HTML
    tree = html.fromstring(document_text)
    sections = html.tostring(tree).split('<hr>')[1:]
    
    obj = {}
    for i in range(len(sections)):
        for trigger in triggers:
            if trigger['keyword'] in sections[i] and trigger['obj_key'] not in obj:
                if trigger['separate_header']:
                    i += 1
                    
                try:
                    obj[trigger['obj_key']] = trigger['parse_func'](sections[i])
                except Exception as e:
                    print " >> {}".format(sections[i])
                    print "Parsing: {} -- {}".format(patent_path, e)
                    exit()
    
    return obj


def clean_str(x):
    return re.sub(r'[\n|\s]+', ' ', x.replace('&nbsp',' ').strip())

def parse_date(section_text):
    months = ['January','February','March','April','May','June',
        'July','August','September','October','November','December']
    months_pattern = '|'.join(months)

    m = re.search(r'({}) ([0-9]+), ([0-9]+)'.format(months_pattern), section_text)
    if m is None:
        raise Exception('Error: failed to parse date')
    
    return m.group(0)

def parse_class(section_text):
    tree = html.fromstring(section_text)
    classes = None
    for node in tree.xpath('//table/tr'):
        if 'CPC Class' in html.tostring(node):
            field, value = node[:2]
            classes = value.text
            break
    
    if classes is None:
        raise Exception('Error: failed to parse class')
    
    return [ clean_str(re.sub(r'\([0-9]+\)','',x)) for x in classes.split(';') ]

def parse_title(section_text):
    tree = html.fromstring(section_text)
    title = None
    for node in tree.xpath('//font'):
        title = node.text.strip()
    
    if title is None:
        raise Exception('Error: failed to parse title')
    
    return title
    
def parse_abstract(section_text):
    tree = html.fromstring(section_text)
    abstract = None
    for node in tree.xpath('//p'):
        abstract = clean_str(node.text) 
    
    if abstract is None:
        raise Exception('Error: failed to parse title')
    
    return abstract

def parse_description(section_text):
    m = re.findall(r'<br><br>\s*?([^<]+)', section_text)
    if m is None:
        raise Exception('Error: failed to parse description')
    
    return '\n'.join([ clean_str(x) for x in m ])

def parse_claims(section_text):
    m = re.findall(r'<br><br>\s*?([^<]+)', section_text)
    if m is None:
        raise Exception('Error: failed to parse claims')
    
    return '\n'.join([ clean_str(x) for x in m ])

def patent_path(patent_number):
    patent_root = str(int(patent_number / 1000))
    return os.path.join('patents', patent_root, '{}.html'.format(patent_number))

if __name__ == '__main__':
    main(parser.parse_args())
