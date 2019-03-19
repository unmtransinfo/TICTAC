#!/usr/bin/env python
##############################################################################
### pubchem_query.py - utility app for the PubChem PUG REST API.
###
###
### Jeremy Yang
###  7 Aug 2014
##############################################################################
import sys,os,re,getopt,types,codecs,time
#
import time_utils
import pubchem_utils
#
PROG=os.path.basename(sys.argv[0])
#
API_HOST='pubchem.ncbi.nlm.nih.gov'
API_BASE_PATH='/rest/pug'
#
#############################################################################
usage='''\
%(PROG)s - (PUG REST client)
required (one of):
        --list_substancesources
        --list_assaysources
        --cpd_smi2id SMILES
        --name2sids ..................... (requires NAME)
        --name2cids ..................... (requires NAME)

requires CIDs:
        --cids2smi ...................... output SMI
        --cids2ism ...................... output isomeric SMI
        --cids2sdf ...................... output SDF
        --cids2props .................... molecular properties
        --cids2inchi .................... InChi + InChiKey
        --cids2synonyms .................
        --cids2sids .....................  
        --cids2assaysummary .............  

requires SIDs:
        --sids2cids .....................  
        --sids2sdf ...................... output SDF
        --sids2assaysummary .............  


requires AIDs:
        --describe_assay ................
        --aid2name ......................
        --assaydescriptions .............

requires AIDs and SIDs:
        --assayresults ..................

options:
	--i IFILE ....................... input IDs file (CID|SID)
	--id ID ......................... input ID (CID|SID)
	--iaid AIDFILE .................. input AIDs file
	--aid AID ....................... input AID
	--name NAME ..................... name query
	--o OFILE .......................
	--api_host HOST ................. [%(API_HOST)s]
	--api_base_path PATH ............ [%(API_BASE_PATH)s]
        --skip N ........................ skip (input IDs)
        --nmax N ........................ max count (input IDs)
        --v ............................. verbose
        --h ............................. this help
'''%{'PROG':PROG,'API_HOST':API_HOST,'API_BASE_PATH':API_BASE_PATH}

def ErrorExit(msg):
  print >>sys.stderr,msg
  sys.exit(1)

##############################################################################
if __name__=='__main__':
  id_query=None; name_query=None; ifile=None; ofile=''; verbose=0;
  aid_query=None; ifile_aid=None;
  describe_assay=False; 
  list_assaysources=False; list_substancesources=False;
  cpd_smi2id=''; 
  sids2cids=False;
  cids2sids=False;
  cids2assaysummary=False;
  sids2assaysummary=False;
  cids2props=False; cids2smi=False; cids2sdf=False; sids2sdf=False; cid2synonyms=False;
  cids2ism=False;
  cids2inchi=False; 
  cids2synonyms=False; aid2name=False; assaydescriptions=False; assayresults=False;
  name2sids=False; name2cids=False;
  skip=0; nmax=sys.maxint;
  dbusr=None; dbpw=None;
  opts,pargs=getopt.getopt(sys.argv[1:],'',['i=','o=',
	'id=', 'iaid=', 'aid=',
	'describe_assay', 'cpd_smi2id=', 'aid2name', 'assaydescriptions', 'assayresults',
	'sids2cids', 'cids2props', 'cids2smi', 'cids2sdf', 'sids2sdf', 'name2sids', 'name2cids',
	'cids2sids','cids2ism',
	'cids2inchi',
	'cids2assaysummary', 
	'sids2assaysummary', 
	'name=', 'cid2synonyms', 'cids2synonyms', 'list_assaysources', 'list_substancesources',
	'api_host=','api_base_path=','dbusr=','dbpw=',
	'skip=', 'nmax=','version=','help','v','vv','vvv'])
  if not opts: ErrorExit(usage)
  for (opt,val) in opts:
    if opt=='--help': ErrorExit(usage)
    elif opt=='--o': ofile=val
    elif opt=='--i': ifile=val
    elif opt=='--iaid': ifile_aid=val
    elif opt=='--id': id_query=int(val)
    elif opt=='--aid': aid_query=int(val)
    elif opt=='--dbusr': dbusr=val
    elif opt=='--dbpw': DBPW=val
    elif opt=='--describe_assay': describe_assay=True
    elif opt=='--aid2name': aid2name=True
    elif opt=='--assaydescriptions': assaydescriptions=True
    elif opt=='--assayresults': assayresults=True
    elif opt=='--cpd_smi2id': cpd_smi2id=val
    elif opt=='--sids2cids': sids2cids=True
    elif opt=='--cids2sids': cids2sids=True
    elif opt=='--cids2props': cids2props=True
    elif opt=='--cids2sdf': cids2sdf=True
    elif opt=='--sids2sdf': sids2sdf=True
    elif opt=='--cids2smi': cids2smi=True
    elif opt=='--cids2ism': cids2ism=True
    elif opt=='--cids2inchi': cids2inchi=True
    elif opt=='--cids2assaysummary': cids2assaysummary=True
    elif opt=='--sids2assaysummary': sids2assaysummary=True
    elif opt=='--name2sids': name2sids=True
    elif opt=='--name2cids': name2cids=True
    elif opt=='--name': name_query=val
    elif opt=='--cid2synonyms': cid2synonyms=True
    elif opt=='--cids2synonyms': cids2synonyms=True
    elif opt=='--list_assaysources': list_assaysources=True
    elif opt=='--list_substancesources': list_substancesources=True
    elif opt=='--api_host': API_HOST=val
    elif opt=='--api_base_path': API_BASE_PATH=val
    elif opt=='--skip': skip=int(val)
    elif opt=='--nmax': nmax=int(val)
    elif opt=='--v': verbose=1
    elif opt=='--vv': verbose=2
    elif opt=='--vvv': verbose=3
    else: ErrorExit('Illegal option: %s'%(opt))

  BASE_URI='https://'+API_HOST+API_BASE_PATH

  if ofile:
    fout=open(ofile,"w+")
    #fout=codecs.open(ofile,"w","utf8","replace")
    if not fout: ErrorExit('ERROR: cannot open outfile: %s'%ofile)
  else:
    fout=sys.stdout
    #fout=codecs.getwriter('utf8')(sys.stdout,errors="replace")

  ids=[]
  if ifile:
    fin=open(ifile)
    if not fin: ErrorExit('ERROR: cannot open ifile: %s'%ifile)
    while True:
      line=fin.readline()
      if not line: break
      try:
        ids.append(int(line.rstrip()))
      except:
        print >>sys.stderr, 'ERROR: bad input ID: %s'%line
        continue
    if verbose:
      print >>sys.stderr, '%s: input IDs: %d'%(PROG,len(ids))
    fin.close()
    id_query=ids[0]
  elif id_query:
    ids=[id_query]

  aids=[]
  if ifile_aid:
    fin=open(ifile_aid)
    if not fin: ErrorExit('ERROR: cannot open ifile: %s'%ifile_aid)
    while True:
      line=fin.readline()
      if not line: break
      try:
        aids.append(int(line.rstrip()))
      except:
        print >>sys.stderr, 'ERROR: bad input AID: %s'%line
        continue
    if verbose:
      print >>sys.stderr, '%s: input AIDs: %d'%(PROG,len(aids))
    fin.close()
    aid_query=aids[0]
  elif aid_query:
    aids=[aid_query]

  t0=time.time()

  if describe_assay:
    pubchem_utils.DescribeAssay(BASE_URI,aid_query,verbose)

  elif list_assaysources:
    pubchem_utils.ListAssaySources(BASE_URI,fout,verbose)

  elif list_substancesources:
    pubchem_utils.ListSubstanceSources(BASE_URI,fout,verbose)

  #elif cid2synonyms:
  #  if not id_query: ErrorExit('ERROR: CID required\n'+usage)
  #  synonyms = pubchem_utils.Cid2Synonyms(BASE_URI,id_query,verbose)
  #  synonyms = pubchem_utils.SortCompoundNamesByNiceness(synonyms)
  #  for s in synonyms:
  #    print '%d: %s'%(id_query,s)

  elif cids2synonyms:
    if not ifile: ErrorExit('ERROR: CID[s] required\n'+usage)
    pubchem_utils.Cids2Synonyms(BASE_URI,ids,fout,skip,nmax,verbose)

  elif cpd_smi2id:
    print pubchem_utils.Smi2Cid(BASE_URI,cpd_smi2id,verbose)

  elif sids2cids:
    #sids=map(lambda x:int(x),re.split(r'\s*,\s*',sids2cids))
    pubchem_utils.Sids2CidsCSV(BASE_URI,ids,fout,verbose)

  elif cids2props:
    #cids=map(lambda x:int(x),re.split(r'\s*,\s*',cids2props))
    pubchem_utils.Cids2Properties(BASE_URI,ids,fout,verbose)

  elif cids2inchi:
    #cids=map(lambda x:int(x),re.split(r'\s*,\s*',cids2props))
    pubchem_utils.Cids2Inchi(BASE_URI,ids,fout,verbose)

  elif cids2sids:
    pubchem_utils.Cids2SidsCSV(BASE_URI,ids,fout,verbose)

  elif name2sids:
    if not name_query: ErrorExit('ERROR: name required\n'+usage)
    sids=pubchem_utils.Name2Sids(BASE_URI,name_query,verbose)
    for sid in sids: print '%d'%sid

  elif name2cids:
    if not name_query: ErrorExit('ERROR: name required\n'+usage)
    cids=pubchem_utils.Name2Cids(BASE_URI,name_query,verbose)
    for cid in cids: print '%d'%cid

  elif aid2name:
    if not aid_query: ErrorExit('ERROR: AID required\n'+usage)
    xmlstr=pubchem_utils.Aid2DescriptionXML(BASE_URI,aid_query,verbose)
    name,source = pubchem_utils.AssayXML2NameAndSource(xmlstr)
    print '%d:\n\tName: %s\n\tSource: %s'%(aid2name,name,source)

  elif assaydescriptions:
    if not aid_query: ErrorExit('ERROR: AID[s] required\n'+usage)
    pubchem_utils.GetAssayDescriptions(BASE_URI,aids,fout,skip,nmax,verbose)

  elif assayresults:
    if not aid_query: ErrorExit('ERROR: AID[s] required\n'+usage)
    if not id_query: ErrorExit('ERROR: SID[s] required\n'+usage)
    #n_in,n_out = pubchem_utils.GetAssayResults_Screening(BASE_URI,aids,ids,fout,skip,nmax,verbose)
    #print >>sys.stderr, '%s,%s: aids in: %d ; results out: %d'%(ifile,ofile,n_in,n_out)

    pubchem_utils.GetAssayResults_Screening2(BASE_URI,aids,ids,fout,skip,nmax,verbose)

  elif cids2sdf:
    if not id_query: ErrorExit('ERROR: CID[s] required\n'+usage)
    pubchem_utils.Cids2Sdf(BASE_URI,ids,fout,verbose)

  elif cids2assaysummary:
    if not id_query: ErrorExit('ERROR: CID[s] required\n'+usage)
    pubchem_utils.Cids2Assaysummary(BASE_URI,ids,fout,verbose)

  elif sids2assaysummary:
    if not id_query: ErrorExit('ERROR: SID[s] required\n'+usage)
    pubchem_utils.Sids2Assaysummary(BASE_URI,ids,fout,verbose)

  elif cids2smi:
    if not id_query: ErrorExit('ERROR: CID[s] required\n'+usage)
    pubchem_utils.Cids2Smiles(BASE_URI,ids,False,fout,verbose)

  elif cids2ism:
    if not id_query: ErrorExit('ERROR: CID[s] required\n'+usage)
    pubchem_utils.Cids2Smiles(BASE_URI,ids,True,fout,verbose)

  elif sids2sdf:
    n_sid_in,n_sdf_out = pubchem_utils.Sids2Sdf(BASE_URI,ids,fout,skip,nmax,verbose)
    print >>sys.stderr, '%s,%s: sids in: %d ; sdfs out: %d'%(ifile,ofile,n_sid_in,n_sdf_out)

  else:
    ErrorExit('ERROR: no operation specified.\n'+usage)

  if verbose:
    print >>sys.stderr, ("total elapsed time: %s"%(time_utils.NiceTime(time.time()-t0)))
