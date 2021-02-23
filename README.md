# sample_sorter

Program to sort sample names according to an ontology, with regexpes. Default usage takes a as inputs: a .tsv list of sample names, a .yaml describing the ontology and associated regular expressions.


## Usage

Use option `-h` / `--help` to see available command-line options:

```console
dr-david@cbg:~$ python ./sample_sorter.py -h
usage: sample_sorter.py [-h] -s TSV) (-y YML [-l TXT] [-t TSV] [-d] [-f] [-v]

Sort sample names into ontologies.

optional arguments:
  -h, --help            show this help message and exit
  -s TSV, --samples TSV
                        V-pipe samples list tsv
  -y YML, --onto YML    Yaml file of ontologies.
  -l TXT, --list TXT    Output results to as a txt file where each line
                        contains a list of the samples ontologies.
  -t TSV, --tsv TSV     Output results to as a tsv file where columns are
                        partial ontologies and lines are samples.
  -d, --dump            Dump the ontology list to the terminal
  -f, --force           Do not check for conflict between ontologies.
  -v, --verbose         Write what's happening in the terminal.
```

## Examples

We will use dummy data in the directory `./dummydata` to illustrate usage. We have a dummy sample list in `./dummydata/dummy.tsv`, that we want to sort according to the ontology in `./dummydata/dummy2.yaml`:
```console
dr-david@cbg:~$ cat ./dummydata/dummy.tsv
ctrl1	batch1
ctrl2	batch1
waste1	batch1
waste2	batch1
clinic1	batch1
clinic2	batch1
dr-david@cbg:~$ cat ./dummydata/dummy2.yaml
control: ctr
sample:
  clinical: clinic
  wastewater: waste
```
