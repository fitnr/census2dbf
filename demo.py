from dbfpy import dbf as dbfpy
from dbfpy import dbfnew as dbfnew
import sys


def main():
    dbfn = dbfnew.dbf_new()

    dbfn.add_field("name", 'C', 80)
    dbfn.add_field("price", 'N', 10, 2)
    dbfn.add_field("date", 'D', 8)
    dbfn.write("tst.dbf")
    # test new dbf
    print "*** created tst.dbf: ***"
    dbft = dbfpy.Dbf()
    dbft.openFile('tst.dbf', readOnly=0)
    dbft.reportOn()

    # add a record
    rec = dbfnew.DbfRecord(dbft)
    rec['name'] = 'something'
    rec['price'] = 10.5
    rec['date'] = (2000, 1, 12)
    rec.store()
    # add another record
    rec = dbfpy.DbfRecord(dbft)
    rec['name'] = 'foo and bar'

    rec['price'] = 12234
    rec['date'] = (1992, 7, 15)
    rec.store()
    dbft.close()

if __name__ == "__main__":
    sys.exit(main())
