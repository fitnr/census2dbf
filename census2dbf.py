#!/usr/bin/env python
# encoding: utf-8
"""
csv2dbf.py
Created by Neil Freeman on 2012-06-10.
"""

import sys
import argparse
import dbf
import csv
import re

help_message = '''Convert CSV to DBF. Requires python dbf library: http://pypi.python.org/pypi/dbf/'''


class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg


def detect_census(handle):
    reader = csv.reader(handle)
    for i in range(10):
        row = next(reader)

    # Reset handle to start.
    handle.seek(0)
    if re.match(r'\d{7}US\d{2}', row[0]) is not None:
        return True  # We found some census data!
    else:
        return False


def parse_header(header):
    fields = header.strip().split(',')
    fields = [f[:11] for f in fields]  # Clip each field to 11 characters.
    # Replace illegal characters in fields with underscore.
    illegal = re.compile(r'[^\w]')
    return [illegal.sub('_', x) for x in fields]


def parse_field_lengths(handle):
    reader = csv.reader(handle)
    lengths = next(reader)
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
    input_handle = args.input
    header = input_handle.next()
    headers = parse_header(header)

    quote_minimal_reader = csv.reader(input_handle, quoting=csv.QUOTE_MINIMAL)
    quote_minimal_rows = quote_minimal_reader.next()
    # Reset to the first row to read it with csv module.
    input_handle.seek(0)
    input_handle.next()
    try:
        quote_nonnumeric_reader = csv.reader(input_handle, quoting=csv.QUOTE_NONNUMERIC)
        # stringreader will that a bunch of ints are float, but is correct about strings.
        quote_nonnumeric_rows = quote_nonnumeric_reader.next()
    except ValueError:
        sys.exit("Could not process document.\nPlease make sure that fields are properly escaped.")

    # Calculate field lengths
    field_lengths = parse_field_lengths(input_handle)

    two_rows = zip(quote_nonnumeric_rows, quote_minimal_rows)
    field_types = []

    decimal = re.compile(r'\.')

    for x in two_rows:
        if isinstance(x[0], str) and isinstance(x[1], str):
            field_types.append('C')

        elif decimal.search(x[1]):
            field_types.append('F')

        else:
            field_types.append('N')

    #print dbf_fields

    input_handle.seek(0)
    input_handle.next()

    reader = csv.reader(input_handle, quoting=csv.QUOTE_MINIMAL)
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
