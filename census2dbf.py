#!/usr/bin/env python
# encoding: utf-8
"""
csv2dbf.py

Created by neil freeman on 2012-06-10.
"""

import sys
import argparse
import dbf
import csv
import re

help_message = '''
Convert CSV to DBF.
'''

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

def parse_header(header):
    header = header.strip()
    fields = header.split(',')
    illegal = re.compile(r'[^\w]')
    # Clip each field to 11 characters.
    fields = [f[:11] for f in fields]
    # Replace illegal characters in fields with underscore.
    fields = [illegal.sub('_', x) for x in fields]
    return fields

def parse_field_lengths(handle):
    reader = csv.reader(handle)
    lengths = reader.next()
    lengths = [len(x) for x in lengths]
    for row in reader:
        e = enumerate(row)
        for x, y in e:
            lengths[x] = max(lengths[x], len(y))
    return lengths

def main(argv=None):
    description = 'Convert CSV to DBF.'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('input', type=argparse.FileType('rb', 0), help='input csv')
    parser.add_argument('output', type=argparse.FileType('wb', 0), help='output dbf')
     
    args = parser.parse_args()
    # Pull the first row for processing into field names. Pull the second row for comparing int and float.
    header = args.input.next()
    headers = parse_header(header)
     
    quote_minimal_reader = csv.reader(args.input, quoting=csv.QUOTE_MINIMAL)
    quote_minimal_rows = quote_minimal_reader.next()
    # Reset to the first row to read it with csv module.
    args.input.seek(0)
    args.input.next()
    try: 
        quote_nonnumeric_reader = csv.reader(args.input, quoting=csv.QUOTE_NONNUMERIC)
        # stringreader will that a bunch of ints are float, but is correct about strings.
        quote_nonnumeric_rows = quote_nonnumeric_reader.next()        
    except ValueError:
        sys.exit("Could not process document.\nPlease make sure that all strings fields are enclosed with double quotes (\"example\").")
     
    # Calculate field lengths 
    field_lengths = parse_field_lengths(args.input)
  
    two_rows = zip(quote_nonnumeric_rows, quote_minimal_rows)
    field_types = []
    """
     dbf field types are described here: http://www.clicketyclick.dk/databases/xbase/format/data_types.html
     this converter will only concern itself with the below three. Sorry DATETIME.
     C[haracter] aka Str, N[umber] aka Int, F[loat]
    """
    decimal = re.compile(r'\.')
    
    for x in two_rows:
        if isinstance(x[0], str) and isinstance(x[1], str) :
            field_types.append('C')
            
        elif decimal.search(x[1]):
            field_types.append('F')
            
        else:
            field_types.append('N')
        
    #print dbf_fields
    
    args.input.seek(0)
    args.input.next()
    
    reader = csv.reader(args.input, quoting=csv.QUOTE_MINIMAL)
    records = []
    for row in reader:
        records.append(row)
    
    field_defs = zip(field_types, field_lengths)
    precision = lambda x: 2 if (x == 'F') else 0
    field_defs = [(x, y, precision(x)) for x, y in field_defs]
    print records[:2]
    db = dbf.dbfwriter(args.output, headers, field_defs, records)
    

if __name__ == "__main__":
    sys.exit(main())
