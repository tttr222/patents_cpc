# U.S. Patents - Harvester and Parser

The code here performs two tasks:

1. Downloads U.S. patents documents from the USPTO website and stores them locally as HTML documents.
2. Parses locally-stored patent documents to a readable JSON or HTML format.

This is used to generate the dataset release here:
http://patents.tttran.net/

Python packages required:
~~~
requests
lxml
~~~

# To recreate the released datasets:

To use this code, you need to know the range of patent numbers you wish to download. That is, you cant choose specific date ranges, but you can download by a range of patent numbers corresponding to the date range. 

# Harvesting

For example, to download all of the 2010 patents you need to know that the first patent in 2010 is numbered *7640598* and the last patent in 2010 is numbered *7861316*. You can then run the following code to harvest the files:

`python patent_harvest.py --start=7640598 --end=7861316`

Likewise, for 2010 the patent range is 7640598 and 8087093:

`python patent_harvest.py --start=7861317 --end=8087093`

# Parsing

Once downloaded, run the following command to generate the 2010 dataset:

`python patent_parse.py --start=7640598 --end=7861316 --outfile=patent_dataset_2010.jsonl`

And for the 2011 dataset:

`python patent_parse.py --start=7861317 --end=8087093 --outfile=patent_dataset_2011.jsonl`

Files are saved in *json lines* format: http://jsonlines.org/

# Caveat

Please note that the parsing code is not designed to be able to parse all patent documents released by the USPTO website. Some of the older patents have inconsistent formatting (and broken HTML) that makes parsing difficult, but not impossible. Some adjustment to the code might be needed to handle older (and possibly newer) patents.

# Author

> Tung Tran  
> tung.tran **[at]** uky.edu  
> <http://tttran.net/>

