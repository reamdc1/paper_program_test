#!/usr/bin/python

import os

#this function will return all of the files that are in a directory. os.walk is recursive traversal.
def returnRecursiveDirFiles(root_dir):
    result = []
    for path, dir_name, flist in os.walk(root_dir):
        for f in flist:
            fname = os.path.join(path, f)
            if os.path.isfile(fname):
                result.append(fname)
    return result

def make_operon_gene_dict(fname):
    result = {}
    for line in [i.strip() for i in open(fname).readlines()]:
        tmp = line.split('\t')
        name = tmp[0]
        genes = tmp[1:]
        result.update({name:genes})
    return result

#assumes that only the gene string and no formatting characters are included
def split_into_signed_genes(line, gene_list):
    result = []
    new_group = True
    cnt = 0
    prefix = ''
    store = []
    already_seen = []
    while cnt < len(line):
        if new_group:
            if line[cnt] == '<':
                strand = -1
                prefix = line[cnt + 1: cnt + 4]
                cnt += 4
                new_group = False
            elif line[cnt] == ' ':
                cnt += 1
                #print store
                result.append(' '.join(store + ['|']))
                store = []
            else:
                strand = 1
                prefix = line[cnt: cnt + 3]
                cnt += 3
                new_group = False
            #print line, strand, prefix, cnt
        else:
            if line[cnt] == '>':
                new_group = True
                cnt += 1
            elif line[cnt] == '-':
                prefix = line[cnt + 1: cnt + 4]
                cnt += 4
            elif line[cnt] == ' ':
                new_group = True
                result.append(' '.join(store + ['|']))
                store = []
                cnt += 1
            else:
                gene = prefix + line[cnt]
                if gene not in already_seen:
                    already_seen.append(gene)
                    if strand == 1:
                        store.append(gene)
                    else:
                        store.append('-' + gene)
                #result.append(store)
                cnt += 1
    result.append(' '.join(store + ['|']))
    print "already seen", already_seen, "gene_list", gene_list
    for gene in gene_list:
        if gene not in already_seen:
            result.append(gene + ' |')
            print "Missing gene", gene
    #res = '\n'.join(result + ['|'])# this tells unimog that we have a linear genome that we are working with
    res = '\n'.join(result)# this tells unimog that we have a linear genome that we are working with
    #print result
    #print res
    return res, result
    


r_dir = './optimized_results_proteobacteria/'
def main():
    
    flist = returnRecursiveDirFiles(r_dir)
    out_folder = './processed_for_unimog/'
    
    operon_name_gene_dict = make_operon_gene_dict('./operon_name_and_genes.txt')
    
    #print operon_name_gene_dict
    
    for fname in flist:
        operon_name = fname.split('/')[-1].split('.')[0]
        #print operon_name_gene_dict[operon_name]
        result = []
        lines = [i.strip() for i in open(fname).readlines()]
        for line in lines:
            if line[0] == '+':
                #result.append(org_name + '\t' + line.split('\t')[1])
                #result.append('>' + NC + '|' + org_name )
                result.append('>' + org_name + '|' + NC )
                #result.append(line.split('\t')[1])
                
                unimog_line, gene_list = split_into_signed_genes(line.split('\t')[1], operon_name_gene_dict[operon_name])
                result.append(unimog_line)
            else:
                #print line.split('\t')
                org_name = line.split('\t')[1]
                NC = line.split('\t')[0]
            
        handle = open(out_folder + operon_name + '.txt', 'w')
        handle.write('\n'.join(result) )
        handle.close()


if __name__ == '__main__':
    main()
