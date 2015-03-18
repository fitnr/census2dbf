#!/usr/bin/env python
# encoding: utf-8
# Adapted from: http://code.activestate.com/recipes/362715-dbf-reader-and-writer/
# From activestate TOS:
# All Content deposited shall to be governed by the Creative Commons 3.0 BY SA (aka CC 3.0 BY SA).
# This license can be found at http://creativecommons.org/licenses/by-sa/3.0/

import datetime
import struct

def spec(typ):
    '''Translate a python type into a DBF spec
        C for ascii character data
        M for ascii character memo data (real memo fields not supported)
        D for datetime objects
        N for ints or decimal objects
        L for logical values 'T', 'F', or '?'
    '''

    if typ == float:
        typ, deci = 'N', 2

    elif typ == int:
        typ, deci = 'N', 0

    elif typ == bool:
        typ, deci = 'L', 0

    elif typ == datetime.datetime:
        typ, deci = 'D', 0

    else:
        typ, deci = 'C', 0

    return typ, deci

def _packheader(fieldspecs, numrows=None, records=None):
    '''Set up header info'''
    ver = 3
    now = datetime.datetime.now()
    year, mon, day = now.year - 1900, now.month, now.day

    if numrows is None:
        numrows = len(records)

    validfieldspecs = [f for f in fieldspecs if f]
    lenheader = len(validfieldspecs) * 32 + 33
    lenrecord = sum(x.get('size', 0) for x in validfieldspecs) + 1

    return struct.pack('<BBBBLHH20x', ver, year, mon, day, numrows, lenheader, lenrecord)

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

def dbfwriter(handle, fields, records, numrows=None, nulls=None):
    """ Return a string suitable for writing directly to a binary dbf file.

    File f should be open for writing in a binary mode.

    Fields should be a dictionary with {names: fieldspec}

    Fieldnames should be no longer than ten characters and not include \x00.

    A valid fieldspec is a dictionary with these keys: type, size, [precision]
        type (python type): float, str, int, datetime, bool
        size (int): the field width

    Fields with empty fieldspec dictionaries will be ignored.

    nulls: values to treat as NULLs

    Records can be an iterable over the records (sequences of field values).
    """
    nulls = set(nulls) or []
    handle.write(_packheader(fields.values(), numrows=numrows, records=records))

    # field specs
    for name, fspec in fields.items():
        if fspec:
            name = name.ljust(11, '\x00')
            fspec['type'], fspec['deci'] = spec(fspec['type'])
            handle.write(struct.pack('<11sc4xBB14x', name, fspec['type'], fspec['size'], fspec['deci']))

    # terminator
    handle.write('\r')

    for row in records:
        handle.write(' ') # deletion flag
        for fspec, value in zip(fields.values(), row):
            if fspec:
                value = _setvalue(value, fspec['type'], fspec['size'], nulls=nulls)
                assert len(value) == fspec['size']
                handle.write(value)

    # End of file
    handle.write('\x1A')

