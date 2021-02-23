import sys
import argparse
import re
import pandas as pd
import yaml

## Argument parser

def parse_args():
    argparser = argparse.ArgumentParser(description="Sort sample names into ontologies.")
    
    # arguments for inputting samples
    input_samples_group = argparser.add_mutually_exclusive_group(required=True)
    input_samples_group.add_argument('-s', '--samples', metavar='TSV',
        type=str, dest='samples', help="V-pipe samples list tsv")

    # arguments for inputting ontology 
    input_ontology_group = argparser.add_mutually_exclusive_group(required=True)
    input_ontology_group.add_argument('-y', '--onto', metavar='YML',
        type=str, dest='onto', help="Yaml file of ontologies.")

    # arguments for outputting
    argparser.add_argument('-l', '--list', metavar='TXT', required=False, default=None,
        type=str, dest='txtout', help="Output results to as a txt file where each line contains a list of the samples ontologies.")
    argparser.add_argument('-t', '--tsv', metavar='TSV', required=False, default=None,
        type=str, dest='tsvout', help="Output results to as a tsv file where columns are partial ontologies and lines are samples.")
    argparser.add_argument('-d', '--dump',
        action="store_true", dest='dump', help = "Dump the ontology list to the terminal")

    # other arguments
    argparser.add_argument('-f', '--force',
        action="store_true", dest='force', help = "Do not check for conflict between ontologies.")  
    argparser.add_argument('-v', '--verbose',
        action="store_true", dest='verbose', help = "Write what's happening in the terminal.")

    args = argparser.parse_args()

    return args


## Functions to input sample names

def load_tsv(tsv_file):
    '''Load sample names from a tsv with columns: sample_name, batch_name
        
    Args:
        tsv_file (str): path to the tsv_file
            
    Returns:
        sample_names (pandas.series): sample names 
    '''
    tsv = pd.read_table(tsv_file, header=None)
    sample_names = tsv.iloc[:,0]
        
    return sample_names

## Function to input sample ontology

def load_yaml(yaml_file):
        '''Load ontology hierarchy dict from a yaml file.

        Args:
            yaml_file (str): path to the yaml file

        Returns
            nested_dict (dict): nested dictionary of ontologies
        '''
        with open(yaml_file, 'r') as f:
            nested_dict = yaml.load(f, Loader=yaml.FullLoader)
        return nested_dict

## Function to parse names etc

def dfs_codes(nested_dict, prepath=()):
    '''Function to compute all depth-first-search (DFS) codes, i.e. paths from root to leaf in a nested dict.
    
    Args:
        nested_dict (dict): nested dictionary 
        prepath (tuple): prepath to append before path
    
    Returns: 
        generator yielding paths, leaves_names (tuple, str): 2-tuple of a path to leaf (tuple) and leaf value (str).
    '''
    for key, val in nested_dict.items():
        path = prepath + (key,) # extend the prepath with the key
        if type(val) != dict: # found leaf
            yield (path, val) # yield the path and the leaf 
        else: # we have a subdictionary 
            yield from dfs_codes(val, path) # yield all paths from recursive call to subdictionary

def make_sample_ontologies(sample_names, ontologies):
    '''Function to make a list of list of ontologies for each sample name.

    Args:
        sample_names (iterable): sample names 
        ontologies (list) : list of ontology, regexp (tuple, str): 2-tuple of an ontology (tuple) and regexp (str).

    Returns:
        sample_ontologies (list): list of lists of different possible ontologies for each sample name
    '''
    sample_ontologies = []
    for sample in sample_names:
        sample_ontology = []
        for ontology in ontologies:
            if re.search(ontology[1], sample) is not None: # if we have a match for this ontology
                sample_ontology.append(ontology[0]) # append the possible ontology
        sample_ontologies.append(sample_ontology) # append the list of possible ontologies for this sample to the list of sample ontologies
    
    return sample_ontologies

def check_conflicts(sample_ontologies):
    '''Check which (if any) samples have multiple ontologies assigned.
    
    Args:
        sample_ontologies (list): list of lists of different possible ontologies for each sample name
    
    Returns:
        conflict_indices (list): list of indices where samples have multiple ontologies assigned
    '''
    onto_num = [len(onto_list) for onto_list in sample_ontologies]
    return [i for i in range(len(onto_num)) if onto_num[i] > 1]

def make_ontologies_df(sample_ontologies):
    '''Convert a list of lists of sample ontologies tuples into a 0-1 dataframe of ontologies.
    
    Args:
        sample_ontologies (list): list of lists of different possible ontologies for each sample name
    
    Returns:
        ontologies_df (pd.DataFrame): df with n_sample rows and p_partial_ontologies columns, with 0-1 entries 
    '''

    return pd.DataFrame([{onto:1 for onto in sum(onto_list, ())} for onto_list in sample_ontologies]).fillna(0).astype("int")


# main function

def main():
    args = parse_args()
    
    # load tsv
    sample_names = load_tsv(args.samples)
    # load yaml
    ontology_dict = load_yaml(args.onto)
    
    # make ontologies of samples
    sample_ontologies = make_sample_ontologies(sample_names, ontologies=list(dfs_codes(ontology_dict)))
    
    # check if we have double ontologies conflicts
    conflicts = check_conflicts(sample_ontologies)
    if args.force == False:
        if len(conflicts) > 0:
            sys.exit("ERROR: Found {} conflicts between sample ontologies, first conflict on sample number {}:\
                \n{} : {}".format(len(conflicts), conflicts[0]+1, sample_names[conflicts[0]], sample_ontologies[conflicts[0]]))

    
    # convert, output
    if args.txtout:
        with open(args.txtout, 'w') as g:
            for line in sample_ontologies:
                for onto in line:
                    g.write(str(onto))
                g.write("\n")
    
    if args.tsvout:
        make_ontologies_df(sample_ontologies).to_csv(args.tsvout, index=False, sep="\t")

    if args.dump:
        for line in sample_ontologies:
            for onto in line:
                print(str(onto), end='')
            print("")

if __name__ == '__main__':
    main()

