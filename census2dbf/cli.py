#!/usr/bin/env python
# encoding: utf-8
from __future__ import print_function
import sys
import os.path
import argparse
from . import censuscsv
from . import dbfwriter

def main():
    '''Command line util for converting census CSV to DBF'''
    parser = argparse.ArgumentParser(description='Convert a US Census csv to dbf.')
    parser.add_argument('input', type=str, help='input csv')
    parser.add_argument('-o', '--output', metavar='dbf', type=str, help='output dbf file. If omitted, dbf will have same name as csv. Use "-" for stdout.')
    parser.add_argument('-i', '--include-cols', metavar='cols', type=str, help='A comma-delimited list of the columns to', default='')
    parser.add_argument('--dd', default=False, action='store_true', help='output a data dictionary made from the header')

    args = parser.parse_args()

    output_file = args.output

    if output_file is None:
        base, _ = os.path.splitext(args.input)
        output_file = base + '.dbf'

    if output_file == '-':
        output_file = sys.stdout
    else:
        print(output_file)

    if args.include_cols:
        include_cols = args.include_cols.split(',')
    else:
        include_cols = None

    with open(args.input, 'r') as handle:
        # Parse the csv.
        fields, numrows, reader = censuscsv.parse(handle, cols=include_cols)

        # Write to dbf.
        with open(output_file, 'w') as sink:
            dbfwriter.dbfwriter(sink, fields, records=reader, numrows=numrows, nulls=censuscsv.NULLS)

    if args.dd:
        dd_file = base + '-data-dictionary.txt'
        print(dd_file, file=sys.stderr)
        censuscsv.write_dd(args.input, dd_file, include_cols=include_cols)


if __name__ == '__main__':
    main()
