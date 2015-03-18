#!/usr/bin/env python
# encoding: utf-8

# Copyright Neil Freeman 2012-15
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import csv
import re
import datetime


def get_header(reader):
    '''extracts the header'''
    fieldnames = []
    row = next(reader)

    patt = re.compile(r'\w{7}US\d+')

    while not patt.match(row[0]):
        fieldnames.append(row)
        row = next(reader)

    return fieldnames


def get_fieldnames(row):
    '''Extract the fieldnames from a Census CSV row'''
    fieldnames = [f[:11] for f in row]  # Clip each field to 10 characters.

    if fieldnames[0] == '':
        fieldnames[0] = 'geoid'

    if fieldnames[1] == '':
        fieldnames[1] = 'geoid2'

    if fieldnames[2] == '':
        fieldnames[2] = 'geoname'

    # Replace illegal characters in fieldnames with underscore.
    illegal = re.compile(r'[^\w]')
    fieldnames = [illegal.sub('', x).lower() for x in fieldnames]

    return fieldnames


def fieldtype(value):
    '''Value should be a string read from the csv.
    Will return value in the (possibly) correct type.'''

    try:
        if float(value) == int(value):
            return int
        else:
            return float
    except ValueError:
        pass

    # Return string as an error
    return str


def spec_fields(names, types, lengths):
    '''Write the spec for DBF fields. Fieldspecs are going to look like: [('C', x), ('N', y, 0)]'''

    specs = []

    for name, (fieldtypes, fieldlengths) in zip(names, zip(types, lengths)):
        deci = ''

        length = max(fieldlengths)
        fieldtypes = set(fieldtypes)

        if name == 'geoid' or name == 'geoid2' or str in fieldtypes:
            typ, deci = 'C', 0

        elif float in fieldtypes:
            typ, deci = 'N', 2

        elif int in fieldtypes:
            typ, deci = 'N', 0


        specs.append(tuple([typ, length, deci]))

    return specs


def dbfspecs(fieldnames, reader):
    '''Inspect fields, determining length and type. Use latter to write DBF specs'''
    lengths, types = [], []

    for row in reader:
        rowtypes, rowlengths = zip(*((fieldtype(cell), len(cell)) for cell in row))

        types.append(rowtypes)
        lengths.append(rowlengths)

    return spec_fields(fieldnames, types, lengths)


def write_dd(input_file, output_file):
    '''Write a data dictionary'''
    now = datetime.datetime.now()

    with open(input_file, 'r') as f:
        headers = get_header(csv.reader(f))

    datadict = zip(*headers)

    with open(output_file, 'w+') as g:
        msg = "Data Dictionary\nAutomatically extracted from the header of {0}\n{1}\n".format(
            input_file, now.strftime("%Y-%m-%d %H:%M"))

        g.write(msg)

        fieldnames = ['field', 'description'] + [''] * (len(datadict[0]) - 2)
        writer = csv.DictWriter(g, fieldnames=fieldnames)

        writer.writerows(datadict)


def parse(input_file):
    """open up the csv, decide what kind of format it is, and get the fields and data ready.
    input: file name
    output: fieldnames, lengths, types, data_dictionary"""

    with open(input_file, 'r') as handle:
        reader = csv.reader(handle)

        # interested in the last row before things it turns into data
        header = get_header(reader)

        fieldnames = get_fieldnames(header[-1])

        # Pointer is on first data row.
        specs = dbfspecs(fieldnames, reader)

        # Pointer is at end.
        # reset pointer back to where data starts
        handle.seek(0)
        for _ in range(len(header)):
            reader.next()

        return fieldnames, specs, reader
