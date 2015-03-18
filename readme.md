# census2dbf

Converts .csv files downloaded from the [Census Factfinder](http://factfinder2.census.gov/) into the legacy [DBF](http://en.wikipedia.org/wiki/DBase) format, which is useful for GIS applications. Census2dbf is a standalone command line tool with no requirements.

## Install

````
pip install census2dbf
````

## Usage

On the shell:

````
$ census2dbf path/to/census.csv --output=/path/of/saved.dbf
path/of/saved.dbf
````

The `--output` argument is optional. If it's omitted, a file with the same name but a .dbf extension will be saved in the same folder. E.g. `census-file.csv` will be converted to a new file named `census-file.dbf`

### Options

#### `--dd`: Data dictionary
Use the `--dd` option to generate a data dictionary from the headers of the census file.
The data dictionary will be saved to the same folder as the output dbf, with a similar name.

Although Census data files usually come with a data dictionary, `census2dbf` will sometimes rewrite fieldnames to avoid duplicates. The data dictionary will match the

````
$ census2dbf --dd tests/data/ACS_13_5YR_S0802_with_ann.csv
tests/data/ACS_13_5YR_S0802_with_ann.dbf
tests/data/ACS_13_5YR_S0802_with_ann-data-dictionary.txt
$ head tests/data/ACS_13_5YR_S0802_with_ann-data-dictionary.txt
Data Dictionary
Automatically extracted from the header of tests/data/ACS_13_5YR_S0802_with_ann.csv
2015-03-18 15:09
GEO.id	Id
...
````

#### `--include-cols`: Filter out columns

Pass the `--include-cols` or `-i` option a comma-delimited list of column names to output only those columns. This option is case-insensitive.

````
$ census2dbf --include-cols geo.id,GEO.id,GEO.id2,HD02_S21 path/to/census.csv
````

