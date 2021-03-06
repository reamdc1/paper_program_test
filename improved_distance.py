#!/usr/bin/python

# I do not know how many of these i need, i will edit later
import Bio
import os
import sys
import math
import subprocess
import cPickle as pickle
import itertools
import time


#this function will return all of the files that are in a directory. os.walk is recursive traversal.
def returnRecursiveDirFiles(root_dir):
    result = []
    for path, dir_name, flist in os.walk(root_dir):
        for f in flist:
            fname = os.path.join(path, f)
            if os.path.isfile(fname):
                result.append(fname)
    return result


def parse_operon_name(operon):
    result = []
    group = operon.split('-')
    for i in group:
       prefix = i[:3]
       genes = i[3:]

       if len(genes) > 0:
           for gene in genes:
               result.append(prefix + gene)
       else:
           result.append(prefix)
    return result

    
# The point of the function is to create a unique string of characters from a list of operon genes.
# This unique string will then be used to calculate the Levinstein edit distance for groups of homologs
# with respect the operon in E.coli. 
def make_operon_gene_string_dict(operon_file = './operon_name_and_genes.txt'):
    result = {}
    
    print operon_file
    for line in [i.strip().split('\t') for i in open(operon_file).readlines()]:
        operon = line[0]
        print operon
        result.update({operon:{'reference_string': ''}})
        
        # Returns the genes in order and a corresponding index. This index will be used to generate the
        # unicode integer of capital letters (as they are lower numerically than lower case).
        
        operon_genes_in_order = parse_operon_name(operon)
        #for gene, index in zip(line[1:], range(0,len(line[1:]))):
        for gene, index in zip(operon_genes_in_order, range(0,len(operon_genes_in_order))):
            print gene
            result[operon].update({gene:chr(65+index)})
            result[operon].update({'reference_string': result[operon]['reference_string'] +  chr(65+index)})
        print operon, result[operon], len(result)
    return result

def parse_operon_result(flist, result_folder):
    
    ignore_list = ['$', '#', '@']
    files_created = []
    
    for fname in flist:
        print fname
        result_name = result_folder + fname.split('/')[-1]
        #print result_name
        nc = ''
        common = ''
        result = []
        for line in [i.strip() for i in open(fname).readlines() if i[0] not in ignore_list]:
            if line[0] == '+':
                operon_line = line.split('\t')[1].strip()
                fixed_operon_line = operon_line.replace('>', '')
                fixed_operon_line = fixed_operon_line.replace('<', '')
                
                new_prefix_char = [' ', '-']
                new_group = True
                i = 0
                gene_list_result = []
                prefix = ''
                while i < len(fixed_operon_line):
                    gene_char = ''
                    if fixed_operon_line[i] in new_prefix_char:
                        new_group = True
                        i+=1
                    if new_group:
                        print "fixed_operon_line", i, fixed_operon_line, fixed_operon_line[i]
                        prefix = ''.join(fixed_operon_line[i:i+3])
                        gene_char = fixed_operon_line[i+3]
                        i += 4
                        gene_list_result.append('*')
                        new_group = False
                    else:
                        gene_char = fixed_operon_line[i]
                        i += 1
                    gene = prefix+gene_char
                    gene_list_result.append(gene)
                print fixed_operon_line, gene_list_result
                    
                        
                
                
                #fixed_operon_line = '*' + fixed_operon_line.replace(' ', '*')
                
                #result.append('\t'.join([nc, common, line.split('\t')[1]]))
                result.append('\t'.join([nc, common, fixed_operon_line]))
            else:
                tmp = line.split('\t')
                nc = tmp[0]
                common = '_'.join(tmp[1].split('_')[:2])
        handle = open(result_name, 'w')
        handle.write('\n'.join(result))
        handle.close()
        files_created.append(result_name)
    return files_created
        
def make_distance_matrix(fname, operon_gene_to_char_dict):
    nc_result_dict = {}
    common_result_dict = {}
    for line in [i.strip() for i in open(fname).readlines()]:
        nc, common, operon = line.split('\t')
        print nc, common, operon
        cnt = dict()
        for i in operon:
            cnt[i] = cnt.get(i, 0) + 1
        
        nc_result_dict.update({nc:cnt})
        common_result_dict.update({common:cnt})
        
    print nc_result_dict['NC_000913']












def main():
    start = time.time()
    
    operon_gene_to_char_dict = make_operon_gene_string_dict('./operon_name_and_genes.txt')
    
    flist = returnRecursiveDirFiles('./optimized_results_proteobacteria/')
    
    created_file_list = parse_operon_result(flist, './operon_string/')
    
    for fname in created_file_list:
        make_distance_matrix(fname, operon_gene_to_char_dict)
    

    print time.time() - start

if __name__ == '__main__':
    main()
