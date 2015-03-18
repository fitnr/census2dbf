#!/usr/bin/env python
# encoding: utf-8
# source: http://code.activestate.com/recipes/362715-dbf-reader-and-writer/
# From activestate TOS:
# All Content deposited shall to be governed by the Creative Commons 3.0 BY SA (aka CC 3.0 BY SA).
# This license can be found at http://creativecommons.org/licenses/by-sa/3.0/

import datetime
import struct

def _packheader(fieldspecs, numrec=None, records=None):
    '''Set up header info'''
    ver = 3
    now = datetime.datetime.now()
    year, mon, day = now.year - 1900, now.month, now.day

    if numrec is None:
        numrec = len(records)

    lenheader = len(fieldspecs) * 32 + 33
    lenrecord = sum(field[1] for field in fieldspecs if field) + 1
    return struct.pack('<BBBBLHH20x', ver, year, mon, day, numrec, lenheader, lenrecord)

def _packspec(name, typ, size, deci):
    name = name.ljust(11, '\x00')
    return struct.pack('<11sc4xBB14x', name, typ, size, deci)

def _setvalue(value, typ, size, nulls=None):
    '''Set a field's value'''

    if nulls and value in nulls:
        value = ''

    if typ == "N":
        value = str(value).rjust(size, ' ')

    elif typ == 'D':
        try:
            value = value.strftime('%Y%m%d')
        except AttributeError:
            value = ''

    elif typ == 'L':
        value = str(value)[0].upper()

    else:
        value = str(value)[:size].ljust(size, ' ')

    return value

def dbfwriter(handle, fields, records, numrec=None, nulls=None):
    """ Return a string suitable for writing directly to a binary dbf file.

    File f should be open for writing in a binary mode.

    Fields should be a dictionary with {names: specs}

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

    If fieldspecs are boolean False, that column is ignored
    """
    fieldspecs = fields.values()
    handle.write(_packheader(fieldspecs, numrec=numrec, records=records))

    # field specs
    for name, spec in zip(fields.keys(), fieldspecs):
        if spec:
            handle.write(_packspec(name, *spec))

    # terminator
    handle.write('\r')

    nulls = set(nulls) or []

    # records
    for row in records:
        handle.write(' ') # deletion flag
        for spec, value in zip(fieldspecs, row):
            if spec:
                value = _setvalue(value, spec[0], spec[1], nulls=nulls)
                assert len(value) == spec[1]
                handle.write(value)

    # End of file
    handle.write('\x1A')

