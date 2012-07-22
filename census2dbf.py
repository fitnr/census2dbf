#!/usr/bin/env python
# encoding: utf-8
"""
csv2dbf.py
Created by Neil Freeman on 2012-06-10.
"""
import sys
import argparse
from dbfpy import dbf as dbfpy
from dbfpy import dbfnew
import csv
import re
import dbfscript

help_message = '''Convert CSV to DBF. Requires python dbf library: http://pypi.python.org/pypi/dbf/'''

"""
def local_from_csv(csvfile='', reader=False, to_disk=False, filename=None,
    field_names=None, extra_fields=None, dbf_type='db3', memo_size=64, min_field_size=1):

    'Adapted from the dbf module to allow for using an open csv reader'
    'creates a Character table from a csv file to_disk will create a table with the same name
    filename will be used if provided field_names default to f0, f1, f2, etc, unless specified (list)
    extra_fields can be used to add additional fields -- should be normal field specifiers (list)'

    if not reader:
        reader = csv.reader(open(csvfile))
    if field_names:
        if ' ' not in field_names[0]:
            field_names = ['%s M' % fn for fn in field_names]
    else:
        field_names = ['f0 M']
    print 'field_names:\n' + str(field_names)
    mtable = dbf.Table(':memory:', [field_names[0]], dbf_type=dbf_type, memo_size=memo_size)
    fields_so_far = 1
    for row in reader:
        while fields_so_far < len(row):
            if fields_so_far == len(field_names):
                field_names.append('f%d M' % fields_so_far)
            mtable.add_fields(field_names[fields_so_far])
            fields_so_far += 1
        mtable.append(tuple(row))
    if filename:
        to_disk = True

    if not to_disk:
        if extra_fields:
            mtable.add_fields(extra_fields)
    else:  # If writing to disk.
        if not filename:
            filename = os.path.splitext(csvfile)[0]
        length = [min_field_size] * len(field_names)
        for record in mtable:
            for i in dbf.index(record.field_names):
                length[i] = max(length[i], len(record[i]))
        fields = mtable.field_names
        print 'mtable.field_names:\n' + str(fields)
        fielddef = []
        for i in dbf.index(length):
            if length[i] < 255:
                fielddef.append('%s C(%d)' % (fields[i], length[i]))
            else:
                fielddef.append('%s M' % (fields[i]))
        if extra_fields:
            fielddef.extend(extra_fields)
        csvtable = dbf.Table(filename, fielddef, dbf_type=dbf_type)
        for record in mtable:
            csvtable.append(record.scatter_fields())
        return csvtable
    return mtable

"""


class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg


class parse_csv(object):
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
            if (0 == k):
                header = row
            full_header.append(row)

        header = [f[:11] for f in header]  # Clip each field to 11 characters.
        if header[0] == '':
            header[0] = 'geoid'
        if header[1] == '':
            header[1] = 'geoid2'
        if header[2] == '':
            header[2] = 'geoname'
        # Replace illegal characters in header with underscore.
        illegal = re.compile(r'[^\w]')
        full_header = zip(*full_header)
        header = [illegal.sub('_', x) for x in header]
        return full_header, header

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
        fields = zip(header, lengths)
        for fieldname, length in fields:

            if (first_num_field > 0):
                x = tuple([fieldname, 'C', length])
                first_num_field -= 1
            else:
                x = tuple([fieldname, 'N', length])

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


def main(argv=None):
    description = 'Convert CSV to DBF.'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('input', type=argparse.FileType('rb', 0), help='input csv')
    parser.add_argument('output', help='output dbf file name')
    parser.add_argument('output_dd', default=False, help='output a data dictionary made from the header')

    args = parser.parse_args()

    csv_parser_args = {
        'handle': args.input
    }
    csv_parser = parse_csv(**csv_parser_args)
    num_header_rows = csv_parser.find_first_data_row()

    data_dictionary, header = csv_parser.parse_header(num_header_rows)

    lengths = csv_parser.parse_field_lengths(num_header_rows)

    first_num_field = csv_parser.find_first_num_field(num_header_rows)

    # Write the field specs.
    fieldspecs = csv_parser.spec_fields(header, first_num_field, lengths)

    #place pointer in the right place
    csv_parser.point_at_data(num_header_rows)

    #local_from_csv(reader=csv_parser.reader, field_names=fieldspecs, filename=args.output, dbf_type='dbf')
    #mtable = local_from_csv(reader=csv_parser.reader, field_names=fieldspecs, dbf_type='dbf')
    #mtable = local_from_csv(reader=csv_parser.reader, dbf_type='dbf')
    '''
    fields = ['GEOid', 'GEOid2','GEOdisplaylabel','S01','S01','S02','S02','S03','S03','S04','S04','S05','S05','S06','S06','S07','S07','S08','S08','S09','S09','S10','S10','S11','S11','S12','S12','S13','S13','S14','S14','S15','S15','S16','S16','S17','S17','S18','S18','S19','S19','S20','S20','S21','S21','S22','S22','S23','S23','S24','S24','S25','S25','S26','S26','S27','S27','S28','S28','S29','S29','S30','S30','S31','S31','S32','S32','S33','S33','S34','S34','S35','S35','S36','S36','S37','S37','S38','S38','S39','S39','S40','S40','S41','S41','S42','S42','S43','S43','S44','S44','S45','S45','S46','S46','S47','S47','S48','S48','S49','S49','S50','S50','S51','S51'
    ]
    '''
    #mtable = dbf.from_csv(csvfile='test2.csv', filename=args.output, field_names=fields)
    dbf = dbfnew.dbf_new()

    for field in fieldspecs:
        dbf.add_field(*field)
    try:
        dbf.write('output.dbf')
    except:
        print "couldn't write the dbf. that's a problem"

    dbft = dbfpy.Dbf('output.dbf')
    #dbft.openFile('output.dbf', readOnly=0)
    #dbft.reportOn()

    for row in csv_parser.reader:
        rec = dbfpy.DbfRecord(dbft)
        i = 0
        for fieldname, x, y in fieldspecs:
            rec[fieldname] = row[i]
            i += 1
        rec.store()

    dbft.close()

    if args.output_dd:
        output = args.output[0:-4] + "_data-dictionary.txt"
        with open(output, 'w+') as data_dict_handle:
            data_dict_handle.write("Data dictionary extracted from the header of " % args.input.name)
            out_list = []
            for row in data_dictionary:
                out_str = ""
                for field in row:
                    out_str = out_str + field + "\t"
                out_list.appen(out_str)
            data_dictionary.writelines(out_str)


if __name__ == "__main__":
    sys.exit(main())
