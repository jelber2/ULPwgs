#!/usr/bin/python

import sys, getopt
import pysam
import os
import numpy as np
import multiprocessing as mp
from datetime import datetime

def get_coverage(gpos:None,bam,output:None,force:False):

   chr=None
   start=None
   end=None

   bamfile = pysam.AlignmentFile(bam, "rb")
   if gpos!=None:
         chr=gpos[0]
         if gpos[1]!=None:
            start=int(gpos[1])-1
            end=int(gpos[1])
   
   cov=bamfile.count_coverage(
      contig=chr,
      start=start,
      stop=end,
      quality_threshold=qt
   )

   baseCount={"A":sum(cov[0]),"C":sum(cov[1]),"G":sum(cov[2]),"T":sum(cov[3])}
   bTotal=baseCount["A"]+baseCount["C"]+baseCount["G"]+baseCount["T"]
   if output!=None:
      if not os.path.exists(output) or force:
         f=open(output,"a")
         f.write("\t".join(map(str,[chr,end,baseCount["A"],baseCount["C"],baseCount["G"],baseCount["T"],bTotal]))+"\n")
         f.close()
      else:
         raise FileExistsError
   else:
      print(chr,end,baseCount["A"],baseCount["C"],baseCount["G"],baseCount["T"],bTotal,sep="\t")
     
 
if __name__ == "__main__":
   bam = None
   gpos=None
   region=[None]*2
   threads = mp.cpu_count() - 1
   qt= 15
   verbose=False
   output=None
   force=False
   try:
      opts, args = getopt.getopt(sys.argv[1:],"h:b:g:c:p:q:t:v:o:f:",["bam=","gpos=","chr=","pos=","qt=","threads=","verbose=","output=","force="])
   except getopt.GetoptError:
      print ('get_coverage.py -b <bam> -g [gpos] -c [chr] -p [pos] -q [qt] -t [threads] -v [verbose] -o [output] -f [force]')
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print ('get_coverage.py -b <bam> -g [gpos] -c [chr] -p [pos] -q [qt] -t [threads] -v [verbose] -o [output] -f [force]')
         sys.exit()
      elif opt in ("-b", "--bam"):
         bam = arg
      elif opt in ("-g", "--gpos"):
         gpos = arg
      elif opt in ("-c", "--chr"):
         region[0] = arg
      elif opt in ("-p", "--pos"):
         region[1] = int(arg)
      elif opt in ("-t", "--threads"):
         if int(arg)<threads:
            threads = int(arg)
      elif opt in ("-q", "--qt"):
         qt = int(arg)
      elif opt in ("-v", "--verbose"):
         verbose = bool(arg)
      elif opt in ("-o", "--output"):
         output = arg
      elif opt in ("-f", "--force"):
         force=bool(arg)

   gposcontent = []
   start=datetime.now()
   if verbose:
      print("• Start Time: ",start)
   
   if gpos!=None:
      if os.path.exists(gpos):
         with open(gpos) as f:
            for line in f:
                  gposcontent.append(line.strip().split())
      else:
         raise ValueError("Path to genomic position file not found")
   elif region[0]!=None:
      gposcontent.append(region)
   else:
      raise ValueError("No genomic position was provided")

   jobs=len(gposcontent)

   if output!=None:
      if not os.path.exists(output) or force:
         f=open(output,"w")
         f.write("#chr\tpos\tA\tC\tG\tT\tdepth\n")
         f.close()
      else:
         raise FileExistsError
   else:
      print("#chr\tpos\tA\tC\tG\tT\tdepth")

   if jobs==1 or threads==1:
      list(map(get_coverage,gposcontent,[bam]*jobs,[output]*jobs,[True]*jobs))
   elif jobs>1:
      with mp.Pool(threads) as thread:
         list(thread.starmap(get_coverage,zip(gposcontent,[bam]*jobs,[output]*jobs,[True]*jobs)))
   end=datetime.now()
  
   if verbose:
      print("• End Time: ",end)
      print("• Run Time: ", end-start)
      print("• Jobs: ", jobs)
      print("• Threads: ", threads)