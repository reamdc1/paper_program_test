#in this version i have removed the seq, as it serves no purpose for what i am doing now
class Homolog:
    """This is a class that will hold the values that i wish to store about homologs"""
    def __init__(self, Accession, Organism, Locus, Gene, Predicted_gene, Synonyms, Eval, Percent_ident, Bits_score, GC, Start, Stop, Strand, Product_type, HGT_candidate = {'likelyhood':'not_eval', 'method': 'none' , 'eval_score': 0.0, 'eval_thresh': 0.0}): #, Seq):
        "This will initialize Homolog, the assumed format is all strings, but i am making an  exception for HGT_candidate here since it is an ad-hoc improvement right now"
        self.__accession = str(Accession)
        self.__organism = str(Organism)
        self.__locus = str(Locus)
        self.__gene = str(Gene)
        self.__predicted_gene = str(Predicted_gene)
        self.__synonyms = Synonyms
        self.__eval = float(Eval)
        self.__percent_ident = float(Percent_ident)
        self.__bits_score = float(Bits_score)
        self.__gc = float(GC)
        self.__start = int(Start)
        self.__stop = int(Stop)
        self.__strand = int(Strand)
        self.__product_type = str(Product_type)
        # i think that this variable should have 4 parameters: going to just dictionary this by name
        # 1) likelyhood :'not_eval' - no evaluation performed. 'probable' - evaluation suggests HGT likely. 
        #    'improbable' - evaluation suggests HGT is unlikely. 'disagreement' - more than one method used, no consensus (for later)
        # 2) method: used to determine which method used in evaluation
        # 3) eval_score
        # 4) eval_thresh
        # I would like this value to be retained as a Dict internally, but i would like to have the ability to read it in as a string which is first ',' separated then ':' separated
        if str(type(HGT_candidate)) == "<type 'dict'>":
            self.__hgt_candidate = HGT_candidate
        else: # txt is assumed... piss off otherwise, you deserve the catastrophic errors the program will throw as a result :)
            self.__hgt_candidate = {}
            tmp = HGT_candidate.replace(' ', '').split(',')
            for i in tmp[:2]:
                self.__hgt_candidate.update({i.split(':')[0]:i.split(':')[1]})
            for i in tmp[2:]:
                self.__hgt_candidate.update({i.split(':')[0]: float(i.split(':')[1])})
                
        #self.__seq = Seq
        
    def accession(self):
        """Return the accession number of the organism where the homolog is detected. The return type is string."""
        return self.__accession
    
    def organism(self):
        """Return the organism's common name of the organism where the homolog is detected. The return type is string."""
        return self.__organism
        
    def locus(self):
        """Return the locus of the homolog detected. The return type is string."""
        return self.__locus
        
    def gene(self):
        return self.__gene
        
    def predicted_gene(self):
        return self.__predicted_gene
        
    def synonyms(self): # i should just standardize this outright.... ugh do this after i a test the new version a bit
        return ':'.join(self.__synonyms)
    
    def e_val(self):
        return self.__eval
        
    def percent_ident(self):
        return self.__percent_ident
    
    def bits_score(self):
        return self.__bits_score
        
    def gc(self):
        return self.__gc
    
    def start(self):
        return self.__start
            
    def stop(self):
        return self.__stop
        
    def strand(self):
        return self.__strand
        
    def product_type(self):
        return self.__product_type
    
    def hgt_candidate(self):
        return self.__hgt_candidate
        
    def hgt_candidate_str(self):
        ret_list = []
        order_list = ['likelyhood', 'method', 'eval_score', 'eval_thresh']
        for att in order_list:
            ret_list.append(att + ':' + str(self.__hgt_candidate[att]))
        return ','.join(ret_list)

    # i have not changed most of these functions to accomodate HGT candidate yet, i would like to define this part more carefully.
    
    def ret_str(self, delim = '\t'):
        return delim.join([self.accession(), self.organism(), self.locus(), self.gene(), self.predicted_gene(), self.synonyms(), str(self.e_val()), str(self.percent_ident()),  str(self.bits_score()), str(self.gc()), str(self.start()), str(self.stop()), str(self.strand()), self.product_type(), self.hgt_candidate_str()])

    def Print(self):
        #length = len(self.seq) - 1
        print self.ret_str()
        
    def ReturnVals(self): # I DO NOT LIKE THIS... 
        return self.accession(), self.organism(), self.locus(), self.gene(), self.predicted_gene(), ':'.join(self.synonyms), self.e_val(), self.percent_ident(), self.bits_score(), self.gc(), self.start(), self.stop(), self.strand(), self.product_type(), self.hgt_candidate_str()
    
    def ReturnHomologStr(self, delim = '\t'):
        result = delim.join([self.accession(), self.organism(), self.locus(), self.gene(), self.predicted_gene(), self.synonyms(), str(self.e_val()), str(self.percent_ident()),  str(self.bits_score()), str(self.gc()), str(self.start()), str(self.stop()), str(self.strand()), self.product_type(), self.hgt_candidate_str()])
        return result
        
    
