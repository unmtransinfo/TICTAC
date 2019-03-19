#!/usr/bin/env python
#############################################################################
### pubchem_mols2ids.py - From PubChem PUG REST API, 
### 
### Input:
###   SMILES|InChI [NAME]
### Output:
###   SMILES|InChI<TAB>[CID|SID]<TAB>[NAME]
###
### ref: http://pubchem.ncbi.nlm.nih.gov/pug_rest/
#############################################################################
### Jeremy Yang
#############################################################################
import os,sys,re,getopt,time
import csv,urllib2

import time_utils
import pubchem_utils

API_HOST="pubchem.ncbi.nlm.nih.gov"
API_BASE_PATH="/rest/pug"
API_BASE_URL="http://"+API_HOST+API_BASE_PATH

#############################################################################
def main():
  global PROG,SCRATCHDIR
  PROG=os.path.basename(sys.argv[0])
  SCRATCHDIR=os.getcwd()+'/data/scratch'
  nchunk=50;

  usage='''
  %(PROG)s - fetch CIDs for input SMILES or InChI (PUG REST client)

  required:
  --i INFILE .............. input molecule file
  --o OUTFILE ............. output IDs file

  options:
  --nmax N ................ maximum N IDs
  --skip N ................ skip N IDs
  --nchunk N .............. IDs per PUG request [%(NCHUNK)d]
  --inchi ................. inchi input (default SMILES)
  --v ..................... verbose
  --vv .................... very verbose
  --h ..................... this help
'''%{'PROG':PROG,'NCHUNK':nchunk}

  def ErrorExit(msg):
    print >>sys.stderr,msg
    sys.exit(1)

  ifile=None; ofile=None; verbose=0; nskip=0; nmax=0; 
  inchi=False;
  opts,pargs = getopt.getopt(sys.argv[1:],'',['h','v','vv','i=','o=','skip=','nmax=','nchunk=','inchi'])
  if not opts: ErrorExit(usage)
  for (opt,val) in opts:
    if opt=='--h': ErrorExit(usage)
    elif opt in ('--i','--in'): ifile=val
    elif opt in ('--o','--out'): ofile=val
    elif opt in ('--n','--nmax'): nmax=int(val)
    elif opt=='--inchi': inchi=True
    elif opt=='--nchunk': nchunk=int(val)
    elif opt=='--skip': nskip=int(val)
    elif opt=='--vv': verbose=2
    elif opt=='--v': verbose=1
    else: ErrorExit('Illegal option: %s'%val)

  if not ifile:
    ErrorExit('input file required\n'+usage)

  fin=file(ifile)
  if not fin:
    ErrorExit('cannot open: %s\n%s'%(ifile,usage))
  if ofile:
    fout=file(ofile,'w')
  else:
    fout=sys.stdout

  print >>sys.stderr, time.asctime()

  t0=time.time()

  ### For each SMILES, query using URI like:
  ### http://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/smiles/CCCC/cids/TXT

  nmol=0; 
  nmol_notfound=0
  n_id=0; 
  n_id_out=0; 
  while True:
    line=fin.readline()
    if not line: break
    nmol+=1
    if nskip and nmol<=nskip:
      continue
    if nmax and nmol>(nmax+nskip): break
    line=line.rstrip()
    fields=line.split()
    if len(fields)<1:
      print >>sys.stderr, 'Warning: bad line; no SMILES [%d]: %s'%(nmol,line)
      continue
    qry=fields[0]
    if len(fields)>1:
      name=re.sub(r'^[^\s]*\s','',line)
    else:
      name='%s'%nmol

    try:
      if inchi:
        cids=pubchem_utils.Inchi2Cids(API_BASE_URL,qry,verbose)
      else:
        cids=pubchem_utils.Smi2Cids(API_BASE_URL,qry,verbose)
    except Exception,e:
      print >>sys.stderr, 'ERROR: REST request failed (%s): %s %s'%(e,qry,name)
      nmol_notfound+=1
      fout.write("%s\tNA\t%s\n"%(qry,name))
      continue

    cids_str=(';'.join(map(lambda x:str(x),cids)))
    fout.write("%s\t%s\t%s\n"%(qry,cids_str,name))
    if len(cids)==1 and cids[0]==0:
      nmol_notfound+=1
    else:
      n_id+=len(cids)
      n_id_out+=n_id

    if nmol>0 and (nmol%100)==0:
      print >>sys.stderr, ("nmol = %d ; elapsed time: %s\t[%s]"%(nmol,time_utils.NiceTime(time.time()-t0),time.asctime()))
    if nmol==nmax:
      break

  fout.close()

  print >>sys.stderr, 'mols read: %d'%(nmol)
  print >>sys.stderr, 'mols not found: %d'%(nmol_notfound)
  print >>sys.stderr, 'ids found: %d'%(n_id)
  print >>sys.stderr, 'ids out: %d'%(n_id_out)
  print >>sys.stderr, ("total elapsed time: %s"%(time_utils.NiceTime(time.time()-t0)))

#############################################################################
if __name__=='__main__':
  #import cProfile
  #cProfile.run('main()')
  main()

