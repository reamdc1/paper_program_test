#!/usr/bin/python

# this is a script that is designed to do the following:
# 1) Take the results we currently have and determine how they would change
# 	if you altered the e-val thresh
# 2) Look into the genbank annotation and see if more genes can be located
#  	that we are currently missing
# 3) Report the differences, and ultimately have the ability to try a better recovery
#	of the relevant data (find as many missing genes as current methods could allow)
# 4) Current data is done soley on 10^-10 there is no intermediate filtering, and this should
#	be changed


# I do not know how many of these i need, i will edit later
import Bio
import re
import os
import sys
from Bio import SeqIO,SeqFeature
from Bio.SeqRecord import SeqRecord
from Bio import Application
from Bio.Application import _Option
from Bio.Blast import NCBIXML
from Bio.Blast import NCBIStandalone
from Bio.SeqUtils import GC
import math
from Bio.Align.Applications import ClustalwCommandline
import subprocess
import math
from scipy import stats
from Levenshtein import distance
import cPickle as pickle
import itertools
import time

from homolog import *  #allows me to use "Homolog" without extra refrencing



# Globals - I will likely have more platform-specific tweaks as time progresses
if os.name == "posix":
    gl_new_line = '\n'
else:
    gl_new_line = '\r\n'
    
NUM_PROCESSORS = os.sysconf("SC_NPROCESSORS_CONF") - 1
INTERGENIC_MAX_LENGTH = 200

#this function will return all of the files that are in a directory. os.walk is recursive traversal.
def returnRecursiveDirFiles(root_dir):
    result = []
    for path, dir_name, flist in os.walk(root_dir):
        for f in flist:
            fname = os.path.join(path, f)
            if os.path.isfile(fname):
                result.append(fname)
    return result

# convert a file of format : operon name then a list of the full names of the genes within that operon
# into a dictionary that can be easily accessed or filtered later.
def parse_operon_file(fname):
    result = {}
    
    for line in [i.strip().split('\t') for i in open(fname).readlines()]:
        result.update({line[0]: line[1:]})
        
    return result
    
def parse_operon_file_to_dict(fname):
    result = {}
    
    for line in [i.strip().split('\t') for i in open(fname).readlines()]:
        operon = line[0]
        genes = line[1:]
        result.update({operon: {}})
        for gene in genes:
            result[operon].update({gene:1})
    return result

# This function creates a dictionary indexed by locus from the input genbank file
# and for my purposes now, it will index genes based on their annotation in genbank
# seq_type will allow us to determine the type of sequence returned in for the dict. default
# will be amino acid because this is a lot less noisy.
def return_genbank_dict(gb_file, key = 'annotation', seq_type = 'amino_acid'):
    """Overview: This function will return a dictionary generated from a genbank file with key value supplied by caller.
       Returns: A dictionary created by the supplied genbank file (gb_file) indexed off the key value supplied.
       Default: The deafult key is locus, and this is generally the most useful key type since it is garanteed to be 
       unique within the genbank file. This condition is not necessarily true for any other attribute.
   """
    result = {}
    seq_record = SeqIO.parse(open(gb_file), "genbank").next()
    accession = seq_record.annotations['accessions'][0].split('.')[0]
    common_name = seq_record.annotations['organism'].replace(' ', '_')
    result.update({'accession': accession})
    result.update({'common_name': common_name})
    cnt = 0
    # loop over the genbank file
    unk_cnt = 1
    for fnum, feature in enumerate(seq_record.features):
        # here i simply check the gene coding type, and identify them in a way that can be used later.
        if feature.type == 'CDS' or feature.type == 'ncRNA' or feature.type == 'tRNA' or feature.type == 'mRNA' or feature.type == 'rRNA':
	    start = feature.location._start.position
	       
            stop = feature.location._end.position
            #print start, stop
            strand = feature.strand
            synonyms = 'NONE'
            try: 
                gene = feature.qualifiers['gene'][0]
            except:
                gene = 'unknown'
                
            if 'gene_synonym' in feature.qualifiers:
                synonym_list = feature.qualifiers['gene_synonym'][0].replace(' ', '').split(';')
                synonyms = ':'.join(synonym_list)
            try:
                locus = feature.qualifiers['locus_tag'][0]
            except:
                try:
                    locus = feature.qualifiers['gene'][0]
                except:
                    locus = ''
                    print 'No locus associated. This should never be invoked meaning you are proper fracked. (The gbk file has an error).'
            try:
                seq = feature.qualifiers['translation']
                seq_type = 'Protein'
            except:
                cnt = cnt + 1
                seq = seq_record.seq[start:stop]
                seq_type = feature.type
                if feature.type == 'CDS':
                    seq_type = 'Pseudo_Gene'
            gc = "%2.1f" % GC(seq_record.seq[start:stop])
            # Debugging something odd
            
                #print feature.qualifiers['gene_synonym']
            #method = "exact"
            if key == 'locus':
                result.update({locus: (locus, gene, seq, seq_type, synonyms)})
            elif key == 'annotation':
                if gene == 'unknown':
                    new_gene = 'unknown_' + str(unk_cnt)
                    header = '|'.join([accession, common_name, locus, gene, str(start), str(stop), str(strand), seq_type, synonyms, gc])
                    result.update({new_gene: [header, ''.join(seq)]})
                    unk_cnt +=1
                else:
                    header = '|'.join([accession, common_name, locus, gene, str(start), str(stop), str(strand), seq_type, synonyms, gc])
                    result.update({gene: [header, ''.join(seq)]})
                    try:
                        for syn in synonym_list:
                            result.update({syn: [header, ''.join(seq)]})
                    except:
                        pass

    #print 'The number of non-protein regions in %s is: %i.' % (common_name, cnt)
    return result

# This function will take a list of genbank files and will call a function that will index them
# base on the genbank anotation for the gene name.  (dangerous, since some are misannotated but necessary)
# the return is a dict with the following structure:
# {organism NC: {operon : {gene: [locus, 1]}}} 
# if there are most than one gene with the same annotation, we will not capture this... sorry
def return_org_operon_dict(flist, operon_gene_list_dict):
    result = {}
    
    for fname in flist:
        #print fname
        genbank_dict = return_genbank_dict(fname)
        nc = genbank_dict['accession']
        #print nc
        result.update({nc:{}})
        for operon in operon_gene_list_dict.keys():
            result[nc].update({operon:{}})
            for gene in operon_gene_list_dict[operon]:
                if gene in genbank_dict.keys():
                    locus = genbank_dict[gene][0].split('|')[2]
                    #print locus
                    result[nc][operon].update({gene:[locus, 1]})
                else:
                    result[nc][operon].update({gene:['na', 0]})
    return result
        
# forgive me here, for i have sinned.  to speed up my ability to report the results we want, i am doing this
# quick and dirty... 

def parse_result_filse_for_deletion_reporting(folder):
    result = {}

    flist = returnRecursiveDirFiles(folder)
    
    exclude_list = ['+', '$', '#', '@']
    
    for fname in flist:
        operon = fname.split('/')[-1].split('.')[0]
        result.update({operon:{}})
        print operon
        lines = [i.strip() for i in open(fname).readlines() if i[0] not in exclude_list]
        #print len(lines)
        for line in lines:
            tmp = line.split('\t')
            nc = tmp[0]
            locus = tmp[2]
            annotation = tmp[3]
            blast_predict = tmp[4]
            e_val = tmp[6]
            if nc in result[operon].keys():
                if blast_predict in result[operon][nc].keys():
                    result[operon][nc][blast_predict].append((locus, annotation, blast_predict, e_val))
                else:
                    result[operon][nc].update({blast_predict:[(locus, annotation, blast_predict, e_val)]})
            else:
               result[operon].update({nc:{blast_predict:[(locus, annotation, blast_predict, e_val)]}})
               
    return result

        
def make_report(result_file_dict, organism_operon_gene_dict, operon_gene_list_dict, outfolder):

    #print result_file_dict
    for operon in sorted(result_file_dict.keys()):
        print operon
        operon_length_ref = len(operon_gene_list_dict[operon])
        operon_gene_list_ref = operon_gene_list_dict[operon]
        #print operon_length_ref, operon_gene_list_ref
        for nc in result_file_dict[operon].keys():
            print nc, operon
            #print result_file_dict[operon][nc].keys()
            if nc in organism_operon_gene_dict.keys():#[operon]
                print "len(organism_operon_gene_dict[nc][operon])", len(organism_operon_gene_dict[nc][operon])
            else:
                print "Missing nc", nc
            print operon_length_ref, len(result_file_dict[operon][nc])#, len(organism_operon_gene_dict[nc][operon])
            #if nc in organism_operon_gene_dict[operon].keys():
            #    print "organism_operon_gene_dict[operon][nc]", len(organism_operon_gene_dict[operon][nc])
            for gene in result_file_dict[operon][nc].keys():
                print gene
                if gene in result_file_dict[operon][nc].keys():
                    pass
                    #print 'result_file_dict[operon][nc][gene]', result_file_dict[operon][nc][gene]
                else:
                    pass
                    #print 'Missing', gene
                    #locus, annotation, blast_predict, e_val = result_file_dict[operon][nc][gene]
                    #print gene
                
        

def main():
   start = time.time()
   genbank_folder = '/home/dave/Desktop/all_genbank/'
   nc_filter = [i.strip() for i in open('./filter_test.txt').readlines()]
   
   file_path_list = [i for i in returnRecursiveDirFiles(genbank_folder) if i.split('/')[-1].split('.')[0] in nc_filter]
   
   # keyed {operon_name: {gene:1}}
   operon_gene_dict = parse_operon_file_to_dict('./operon_name_and_genes.txt')
   # keyed {operon_name: [gene_list]})
   operon_gene_list_dict = parse_operon_file('./operon_name_and_genes.txt')
   #print "operon_gene_list_dict",operon_gene_list_dict
   
   #print "file_path_list", len(file_path_list), file_path_list
   
   ## the next 2 lines are only necessary if you need to remake the dict because new genomes have been added
   #organism_operon_gene_dict = return_org_operon_dict(file_path_list, operon_gene_list_dict)
   #pickle.dump(organism_operon_gene_dict, open("organism_operon_gene_dict.p", "wb"))
   
   # only use if the dict has been made and pickled
   organism_operon_gene_dict = pickle.load(open('./organism_operon_gene_dict.p', "rb"))
   #print len(organism_operon_gene_dict['NC_000913']['atpIBEFHAGDC'].keys()), organism_operon_gene_dict['NC_003197']['fucPIKUR']
   
   result_file_dict = parse_result_filse_for_deletion_reporting('./optimized_results_proteobacteria/')
   
   #print result_file_dict['nuoABCEFGHIJKLMN']['NC_002678']
   
   make_report(result_file_dict, organism_operon_gene_dict, operon_gene_list_dict, './missing_genes_files/')
   

   print time.time() - start
if __name__ == '__main__':
    main()
