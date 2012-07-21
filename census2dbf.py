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
from datetime import datetime

help_message = '''Convert CSV to DBF. Requires python dbf library: http://pypi.python.org/pypi/dbf/'''


class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg


class parse_csv():
    # open up the csv, decide what kind of format it is, and get the fields and data ready.
    # input: file handle
    # input (optional): field types, date format
    # output: fieldnames, lengths, types

    def __init__(self, **kwargs):
        self.input_handle = kwargs.get('input_handle')
        self.fields = kwargs.get('fields', None)
        self.date_format = kwargs.get('date_format', None)

    def parse_header(self, header):
        'parses a row and returns fieldnames'
        fields = header.strip().split(',')
        fields = [f[:11] for f in fields]  # Clip each field to 11 characters.
        # Replace illegal characters in fields with underscore.
        illegal = re.compile(r'[^\w]')
        return [illegal.sub('_', x) for x in fields]

    def convert_type(self, value):
        'Value should be a string read from the csv. Will return value in the (possibly) correct type.'
        if self.datetime_format:
            try:
                return datetime.strptime(value, self.datetime_format)
            except ValueError:
                pass

        try:
            return datetime.strptime(value, "%Y/%m/%d")
        except ValueError:
            pass

        try:
            return datetime.strptime(value, "%m/%d/%Y")
        except ValueError:
            pass

        try:
            if float(value) == int(value):
                return int(value)
            else:
                return float(value)
        except ValueError:
            pass

        # Return the string.
        return value

    def parse_field_lengths(self, handle):
        'parses a handle and returns maxlengths of fields in each column'
        reader = csv.reader(handle)
        lengths = next(reader)
        lengths = [len(x) for x in lengths]
        for row in reader:
            e = enumerate(row)
            for x, y in e:
                lengths[x] = max(lengths[x], len(y))
        handle.seek(0)
        return lengths

    def detect_census(self, handle):
        reader = csv.reader(handle)
        for i in range(10):
            row = next(reader)
            if re.match(r'\d{7}US\d{2}', row[0]) is not None:
                handle.seek(0)  # Reset handle to start.
                return True, i  # We found some census data, return the row number

        handle.seek(0)  # Reset handle to start.
        return False, 0

    def read_handle(self):
        census, first_row = self.detect_census()
        if census:
            # Read as a census file.
            # Namely, skip extra header rows and make a data dictionary.
            pass
        pass

    def read_quote_minimal(self):
        'Quote_minimal reads everything as a string'
        header = self.input_handle.next()
        headers = parse_header(header)
        quote_minimal_reader = csv.reader(self.input_handle, quoting=csv.QUOTE_MINIMAL)
        quote_minimal_rows = quote_minimal_reader.next()
        # Reset to the first row to read it with csv module.
        input_handle.seek(0)
        input_handle.next()

    def read_quote_nonnumeric(self):
        try:
            quote_nonnumeric_reader = csv.reader(input_handle, quoting=csv.QUOTE_NONNUMERIC)
            # stringreader will that a bunch of ints are float, but is correct about strings.
            quote_nonnumeric_rows = quote_nonnumeric_reader.next()
        except ValueError:
            sys.exit("Could not process document.\nPlease make sure that fields are properly escaped.")

    def combine_rows(self, non_numeric_rows, minimal_rows):
        two_rows = zip(non_numeric_rows, minimal_rows)
        field_types = []

        decimal = re.compile(r'\.')

        for x in two_rows:
            if isinstance(x[0], str) and isinstance(x[1], str):
                field_types.append('C')

            elif decimal.search(x[1]):
                field_types.append('F')

            else:
                field_types.append('N')

        return field_types
    #print dbf_fields

    reader = csv.reader(self.input_handle, quoting=csv.QUOTE_MINIMAL)
    records = []
    for row in reader:
        records.append(row)

    field_defs = zip(field_types, field_lengths)
    precision = lambda x: 2 if (x == 'F') else 0
    field_defs = [(x, y, precision(x)) for x, y in field_defs]


class output_dbf():
    # uses with dbf class
    # input: fieldnames, lengths, types
    # input: destination file name (optional)
    # output: dbf file
    def __init__(self, **kwargs):
        pass


def main(argv=None):
    description = 'Convert CSV to DBF.'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('input', type=argparse.FileType('rb', 0), help='input csv')
    parser.add_argument('output', type=argparse.FileType('wb', 0), help='output dbf')

    args = parser.parse_args()
    input_handle = args.input

    csv_parser_args = {
        'input_handle': input_handle
    }
    csv_parser = parse_csv(csv_parser_args)

    #csv_parser.dostuff()

    # Calculate field lengths
    field_lengths = csv_parser.parse_field_lengths()

    #db = dbf.dbfwriter(args.output, headers, field_defs, records)


if __name__ == "__main__":
    sys.exit(main())
