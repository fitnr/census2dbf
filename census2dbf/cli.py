#!/usr/bin/env python
# encoding: utf-8

import argparse
import os.path
from . import censuscsv
from . import dbfwriter


def main():
    '''Command line util for converting census CSV to DBF'''
    parser = argparse.ArgumentParser(description='Convert CSV to DBF.')
    parser.add_argument('input', type=argparse.FileType('r', 0), help='input csv', required=True)
    parser.add_argument('-o', '--output', type=argparse.FileType('w', 0), help='output dbf file')
    parser.add_argument('--dd', default=False, action='store_true', help='output a data dictionary made from the header')

    args = parser.parse_args()

    output_file = args.output

    if output_file is None:
        base, _ = os.path.splitext(args.input.name)
        output_file = base + '.dbf'

    with open(output_file, 'w') as sink:

        # Parse the csv.
        fieldnames, fieldspecs, reader = censuscsv.parse(args.input)

        # Write to dbf.
        dbfwriter.dbfwriter(sink, fieldnames, fieldspecs, reader)

        if args.dd:
            dd_file = base + '-data-dictionary.txt'
            censuscsv.write_dd(args.input, dd_file)


if __name__ == '__main__':
    main()
