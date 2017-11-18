# Europarl-sal
Tools for Europarl Parallel Corpus n-way sentence alignment.

To run use:

`python sentence_align.py -i path/to/europarl/files/ -l {list of languages} -m {intersection|union}`

e.g.:

`python sentence_align.py -i Data/ -l en da de -m intersection`

Europarl files should be named in the format `europarl-v7.da-en.da` and can be downloaded from http://www.statmt.org/europarl/ .
Make sure to use "parallel corpus" files and not the source release.