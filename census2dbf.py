#!/usr/bin/env python
# encoding: utf-8
"""
csv2dbf.py
Created by Neil Freeman on 2012-06-10.
Licensed under Creative Commons 3.0 BY SA (aka CC 3.0 BY SA).
http://creativecommons.org/licenses/by-sa/3.0/
"""

import sys
import argparse
import csv
import re
import struct
import datetime
import itertools

help_message = '''Convert Census CSVs to DBF. Requires python dbf library: http://pypi.python.org/pypi/dbf/'''


class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg


def dbfwriter(f, fieldnames, fieldspecs, records):
    """
    source: http://code.activestate.com/recipes/362715-dbf-reader-and-writer/
    From activestate TOS:
    All Content deposited shall to be governed by the Creative Commons 3.0 BY SA (aka CC 3.0 BY SA).
    This license can be found at http://creativecommons.org/licenses/by-sa/3.0/
    """

    """ Return a string suitable for writing directly to a binary dbf file.

    File f should be open for writing in a binary mode.

    Fieldnames should be no longer than ten characters and not include \x00.
    Fieldspecs are in the form (type, size, deci) where
        type is one of:
            C for ascii character data
            M for ascii character memo data (real memo fields not supported)
            D for datetime objects
            N for ints or decimal objects
            L for logical values 'T', 'F', or '?'
        size is the field width
        deci is the number of decimal places in the provided decimal object
    Records can be an iterable over the records (sequences of field values).

    """
    # header info
    ver = 3
    now = datetime.datetime.now()
    yr, mon, day = now.year - 1900, now.month, now.day
    numrec = len(records)
    numfields = len(fieldspecs)
    lenheader = numfields * 32 + 33
    lenrecord = sum(field[1] for field in fieldspecs) + 1
    hdr = struct.pack('<BBBBLHH20x', ver, yr, mon, day, numrec, lenheader, lenrecord)
    f.write(hdr)

    # field specs
    for name, (typ, size, deci) in itertools.izip(fieldnames, fieldspecs):
        name = name.ljust(11, '\x00')
        fld = struct.pack('<11sc4xBB14x', name, typ, size, deci)
        f.write(fld)

    # terminator
    f.write('\r')

    # records
    for record in records:
        f.write(' ')                        # deletion flag
        for (typ, size, deci), value in itertools.izip(fieldspecs, record):
            if typ == "N":
                value = str(value).rjust(size, ' ')
            elif typ == 'D':
                value = value.strftime('%Y%m%d')
            elif typ == 'L':
                value = str(value)[0].upper()
            else:
                value = str(value)[:size].ljust(size, ' ')
            assert len(value) == size
            f.write(value)

    # End of file
    f.write('\x1A')


class csv_parser(object):
    # open up the csv, decide what kind of format it is, and get the fields and data ready.
    # input: file handle
    # input (optional): field types, date format
    # output: fieldnames, lengths, types

    def __init__(self, **kwargs):
        self.handle = kwargs.get('handle')
        self.fields = kwargs.get('fields', None)
        self.reader = csv.reader(self.handle)

    def parse_header(self, num_header_rows):
        'parses a row and returns fieldnames'
        if num_header_rows == 0:
            return False
        self.handle.seek(0)
        full_header = []
        for k in range(num_header_rows):
            row = next(self.reader)
            # pull the fieldnames from the first row of headers
            if (0 == k):
                fieldnames = [f[:11] for f in row]  # Clip each field to 10 characters.
                if fieldnames[0] == '':
                    fieldnames[0] = 'geoid'
                if fieldnames[1] == '':
                    fieldnames[1] = 'geoid2'
                if fieldnames[2] == '':
                    fieldnames[2] = 'geoname'
                # Replace illegal characters in fieldnames with underscore.
                illegal = re.compile(r'[^\w]')
                fieldnames = [illegal.sub('_', x) for x in fieldnames]
                row = fieldnames

            full_header.append(row)
        full_header = zip(*full_header)
        return full_header, fieldnames

    def find_first_data_row(self):
        self.handle.seek(0)
        for i in range(10):
            row = self.reader.next()
            if re.match(r'\d{7}US\d{2}', row[0]):
                self.handle.seek(0)
                # We found some census data, return the row number
                return i
        return False

    def find_first_num_field(self, num_header_rows):
        self.handle.seek(0)
        for i in range(num_header_rows):
            self.reader.next()
        row = self.reader.next()
        # Census files always start with two GEOIDs. Right?
        for j in range(2, len(row)):
            field = row[j]
            try:
                int(field)
                return j
            except ValueError:
                pass
        return False

    def spec_fields(self, header, first_num_field, lengths):
        if self.fields:
            return self.fields
        fieldspecs = []
        # fieldspecs are going to look like: [('stringfield', 'C', x), ('numfield'. 'N', y)]
        for length in lengths:

            if (first_num_field > 0):
                x = tuple(['C', length, 0])
                first_num_field -= 1
            else:
                x = tuple(['N', length, 2])

            fieldspecs.append(x)
        return fieldspecs

    def parse_field_lengths(self, num_header_rows):
        self.handle.seek(0)
        for i in range(num_header_rows):
            self.reader.next()
        lengths = self.reader.next()
        lengths = [len(x) for x in lengths]
        for row in self.reader:
            e = enumerate(row)
            for x, y in e:
                lengths[x] = max(lengths[x], len(y))
        return lengths

    def point_at_data(self, num_header_rows):
        self.handle.seek(0)
        for i in range(num_header_rows):
            self.reader.next()

    def get_records(self):
        #place pointer in the right place
        self.point_at_data(self.num_header_rows)
        return [row for row in self.reader]

    def parse(self):
        num_header_rows = self.find_first_data_row()

        self.data_dictionary, self.header = self.parse_header(num_header_rows)

        lengths = self.parse_field_lengths(num_header_rows)

        first_num_field = self.find_first_num_field(num_header_rows)

        # Write the field specs.
        self.fieldspecs = self.spec_fields(self.header, first_num_field, lengths)

    def write_dd(self, input_file, output_file):
        now = datetime.datetime.now()
        output = new_file_ending(output_file.name, "-data-dictionary.txt")

        with open(output, 'w+') as data_dict_handle:
            msg = "Data Dictionary\nAutomatically extracted from the header of {0}\n{1}\n".format(input_file, now.strftime("%Y-%m-%d %H:%M"))
            data_dict_handle.write(msg)
            out_list = []
            for row in self.data_dictionary:
                out_str = ""
                for field in row:
                    out_str = out_str + field + "\t"
                out_list.append(out_str + "\n")
            data_dict_handle.writelines(out_list)


def new_file_ending(filename, new):
    try:
        k = filename.rindex('.')
        return filename[0:k] + new
    except:
        return filename + new


def main(argv=None):
    description = 'Convert CSV to DBF.'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--input', type=argparse.FileType('r', 0), help='input csv', required=True)
    parser.add_argument('--output', type=argparse.FileType('w', 0), help='output dbf file', required=False)
    parser.add_argument('--dd', default=False, required=False, action='store_true', help='output a data dictionary made from the header')

    args = parser.parse_args()

    output_file = args.output
    if output_file is None:
        name = new_file_ending(args.input.name, '.dbf')
        output_file = open(name, 'w')

    # Parse the csv.
    parse = csv_parser(**{'handle': args.input})
    records = parse.get_records()

    # Write to dbf.
    dbfwriter(output_file, parse.header, parse.fieldspecs, records)

    if args.dd:
        parser.write_dd(parse.data_dictionary, args.input.name, output_file)


if __name__ == "__main__":
    sys.exit(main())
