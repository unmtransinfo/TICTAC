#!/usr/bin/env python
##############################################################################
### DEPRECATED: Should use package https://github.com/chembl/chembl_webresource_client.
##############################################################################
### chembl_inchi_lookup.py -
### See 
### https://www.ebi.ac.uk/chemblws/docs
##############################################################################
### Jeremy Yang
##############################################################################
import sys,os,re,getopt,time,types
import urllib2
import codecs
#
import time_utils
import rest_utils
#
#
PROG=os.path.basename(sys.argv[0])
#
API_HOST='www.ebi.ac.uk'
API_BASE_PATH='/chemblws'
#
#
#############################################################################
def GetByInchikey(id_query,base_uri,verbose=0):
  rval=None
  try:
    rval=rest_utils.GetURL(base_uri+'/compounds/stdinchikey/%s.json'%id_query,{},parse_json=True,verbose=verbose)
  except urllib2.HTTPError, e:
    print >>sys.stderr, 'HTTP Error (%s): %s'%(res,e)
  return rval

##############################################################################
### /chemblws/compounds/stdinchikey/QFFGVLORLPOAEC-SNVBAGLBSA-N
def InchiLookupCompound(ids,api_host,fout,verbose):
  tags = ['chemblId',
	'stdInChiKey',
	'smiles',
	'molecularFormula',
	'species',
	'knownDrug',
	'preferredCompoundName',
	'synonyms',
	'molecularWeight'
	]
  base_url=('http://'+api_host+API_BASE_PATH)
  n_qry=0; n_out=0; n_err=0; 
  fout.write('\t'.join(tags)+'\n')
  for id_this in ids:
    n_qry+=1
    mol=None
    try:
      mol=GetByInchikey(id_this,base_url,verbose)
    except urllib2.HTTPError, e:
      print >>sys.stderr, 'HTTP Error: %s'%(e)
    if not mol or type(mol)!=types.DictType:
      n_err+=1
      continue
    elif not mol.has_key('compound'):
      n_err+=1
      continue

    cpd = mol['compound']

    vals=[]
    for tag in tags:
      vals.append(cpd[tag] if cpd.has_key(tag) else '')
    fout.write('\t'.join([str(val) for val in vals])+'\n')
    n_out+=1

  print >>sys.stderr, 'n_qry: %d'%(n_qry)
  print >>sys.stderr, 'n_out: %d'%(n_out)
  print >>sys.stderr, 'errors: %d'%(n_err)



##############################################################################
if __name__=='__main__':
  asrc=None; atype=None;
  usage='''\
%(PROG)s - ChEMBL REST API client

parameters:
        --i IFILE ................... input InChIs
        --id ID ..................... input InChI
options:
        --o OFILE ................... output file (TSV)
	--api_host HOST ............. [%(API_HOST)s]
	--api_base_path PATH ........ [%(API_BASE_PATH)s]
        --nmax NMAX ................. max records
        --skip SKIP ................. skip 1st SKIP records
        --v[v[v]] ................... verbose [very [very]]
        --h ......................... this help

'''%{	'PROG':PROG,
	'API_HOST':API_HOST,
	'API_BASE_PATH':API_BASE_PATH}

  def ErrorExit(msg):
    print >>sys.stderr,msg
    sys.exit(1)

  id_query=None; ifile=None;
  ofile=None; verbose=0;
  skip=0; nmax=0;
  opts,pargs=getopt.getopt(sys.argv[1:],'',['o=', 'i=', 'id=', 'skip=', 'nmax=',
    'api_host=', 'api_base_path=','h','v','vv','vvv'])
  if not opts: ErrorExit(usage)
  for (opt,val) in opts:
    if opt=='--help': ErrorExit(usage)
    elif opt=='--i': ifile=val
    elif opt=='--id': id_query=val
    elif opt=='--o': ofile=val
    elif opt=='--api_host': API_HOST=val
    elif opt=='--api_base_path': API_BASE_PATH=val
    elif opt=='--skip': skip=int(val)
    elif opt=='--nmax': nmax=int(val)
    elif opt=='--v': verbose=1
    elif opt=='--vv': verbose=2
    elif opt=='--vvv': verbose=3
    else: ErrorExit('Illegal option: %s\n%s'%(opt,usage))

  API_BASE_URI='http://'+API_HOST+API_BASE_PATH

  if ofile:
    fout=codecs.open(ofile,"w","UTF-8","replace")
    if not fout: ErrorExit('ERROR: cannot open outfile: %s'%ofile)
  else:
    fout=codecs.getwriter("UTF-8")(sys.stdout,errors="replace")

  ids=[]
  if ifile:
    fin=open(ifile)
    if not fin: ErrorExit('ERROR: cannot open ifile: %s'%ifile)
    while True:
      line=fin.readline()
      if not line: break
      ids.append(line.rstrip())
    if verbose:
      print >>sys.stderr, '%s: input IDs: %d'%(PROG,len(ids))
    fin.close()
  elif id_query:
    ids.append(id_query)

  if not ids: ErrorExit('ERROR: --id or --ifile required.')

  InchiLookupCompound(ids,API_HOST,fout,verbose)

