census2dbf
====

Converts .csv files downloaded from the [Census Factfinder](http://factfinder2.census.gov/) into the legacy [DBF](http://en.wikipedia.org/wiki/DBase) format, which is useful for GIS applications.

Usage
==

Save to a particular folder, then navigate to the folder and run this shell command: 

`python census2dbf.py --input=/path/to/census.csv --output=/path/of/saved.dbf`

The `--output` argument is optional. If it's omitted, a file with the same name but a .dbf extension will be saved in the same folder. E.g. `census-file.csv` will be converted to a new file called `census-file.dbf`

Use the `--dd` option to generate a data dictionary from the headers of the census file. In the example above, the data dictionary will be saved as `census-file-data-dictionary.txt`.

Automator Workflow
==

The Automator workflow can be used to create a droplet application from census2dbf. Open the workflow in Automator, change the path in the Run Shell Script action to the path where you've saved census2dbf.py. Then save the workflow as an application.