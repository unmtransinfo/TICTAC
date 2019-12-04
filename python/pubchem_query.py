#!/usr/bin/env python3
##############################################################################
### pubchem_query.py - utility app for the PubChem PUG REST API.
###
### Jeremy Yang
##############################################################################
import sys,os,re,argparse,time,logging
#
import time_utils
import pubchem_utils
#
API_HOST='pubchem.ncbi.nlm.nih.gov'
API_BASE_PATH='/rest/pug'
#
#############################################################################

##############################################################################
if __name__=='__main__':
  PROG=os.path.basename(sys.argv[0])

  logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

  ops = [ "list_substancesources", "list_assaysources", "smi2cid", "name2sids",
        "name2cids", "cids2smi", "cids2ism", "cids2sdf", "cids2props", "cids2inchi",
        "cids2synonyms", "cids2sids", "cids2assaysummary", "sids2cids", "sids2sdf",
        "sids2assaysummary", "aid2name", "assaydescribe", "assaydescriptions",
        "assayresults" ]

  parser = argparse.ArgumentParser(description="PubChem PUG REST client")
  parser.add_argument("op",choices=ops,help='operation')
  parser.add_argument("--i", dest="ifile", help="input IDs file (CID|SID)")
  parser.add_argument("--id", dest="id_query", help="input ID (CID|SID)")
  parser.add_argument("--aid", dest="aid_query", help="input AID")
  parser.add_argument("--iaid", dest="ifile_aid", help="input AIDs file")
  parser.add_argument("--name", dest="name_query", help="name query")
  parser.add_argument("--smiles", dest="smi_query", help="SMILES query")
  parser.add_argument("--api_host", default=API_HOST)
  parser.add_argument("--api_base_path", default=API_BASE_PATH)
  parser.add_argument("--skip", type=int, default=0)
  parser.add_argument("--nmax", type=int, default=0)
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("-v", "--verbose", default=0, action="count")
  args = parser.parse_args()

  BASE_URL = 'https://'+args.api_host+args.api_base_path

  if args.ofile:
    fout = open(args.ofile, "w")
  else:
    fout = sys.stdout

  ids=[]
  if args.ifile:
    fin=open(args.ifile)
    if not fin: parser.error('ERROR: cannot open ifile: %s'%args.ifile)
    while True:
      line=fin.readline()
      if not line: break
      try:
        ids.append(int(line.rstrip()))
      except:
        logging.info('ERROR: bad input ID: %s'%line)
        continue
    if args.verbose:
      logging.info('%s: input IDs: %d'%(PROG,len(ids)))
    fin.close()
    id_query=ids[0]
  elif args.id_query:
    ids=[args.id_query]

  aids=[]
  if args.ifile_aid:
    fin=open(args.ifile_aid)
    if not fin: parser.error('ERROR: cannot open ifile: %s'%args.ifile_aid)
    while True:
      line=fin.readline()
      if not line: break
      try:
        aids.append(int(line.rstrip()))
      except:
        logging.info('ERROR: bad input AID: %s'%line)
        continue
    if verbose:
      logging.info('%s: input AIDs: %d'%(PROG,len(aids)))
    fin.close()
    aid_query=aids[0]
  elif args.aid_query:
    aids=[args.aid_query]

  t0=time.time()

  if args.op == 'list_assaysources':
    pubchem_utils.ListAssaySources(BASE_URL, fout, args.verbose)

  elif args.op == 'list_substancesources':
    pubchem_utils.ListSubstanceSources(BASE_URL, fout, args.verbose)

  elif args.op == 'cids2synonyms':
    pubchem_utils.Cids2Synonyms(BASE_URL, ids, fout, args.skip, args.nmax, args.verbose)

  elif args.op == 'cids2props':
    pubchem_utils.Cids2Properties(BASE_URL, ids, fout, args.verbose)

  elif args.op == 'cids2inchi':
    pubchem_utils.Cids2Inchi(BASE_URL, ids, fout, args.verbose)

  elif args.op == 'cids2sids':
    pubchem_utils.Cids2SidsCSV(BASE_URL, ids, fout, args.verbose)

  elif args.op == 'cids2smi':
    pubchem_utils.Cids2Smiles(BASE_URL, ids, False, fout, args.verbose)

  elif args.op == 'cids2ism':
    pubchem_utils.Cids2Smiles(BASE_URL, ids, True, fout, args.verbose)

  elif args.op == 'cids2sdf':
    pubchem_utils.Cids2Sdf(BASE_URL, ids, fout, args.verbose)

  elif args.op == 'cids2assaysummary':
    pubchem_utils.Cids2Assaysummary(BASE_URL, ids, fout, args.verbose)

  elif args.op == 'sids2cids':
    pubchem_utils.Sids2CidsCSV(BASE_URL, ids, fout, args.verbose)

  elif args.op == 'sids2assaysummary':
    pubchem_utils.Sids2Assaysummary(BASE_URL, ids, fout, args.verbose)

  elif args.op == 'sids2sdf':
    n_sid_in, n_sdf_out = pubchem_utils.Sids2Sdf(BASE_URL, ids, fout, args.skip, args.nmax, args.verbose)
    logging.info('%s, %s: sids in: %d ; sdfs out: %d'%(ifile, ofile, n_sid_in, n_sdf_out))

  elif args.op == 'name2sids':
    sids=pubchem_utils.Name2Sids(BASE_URL, args.name_query, args.verbose)
    for sid in sids: print('%d'%sid)

  elif args.op == 'smi2cid':
    if not args.smi_query: parser.error('ERROR: SMILES required')
    print(pubchem_utils.Smi2Cid(BASE_URL, args.smi, args.verbose))

  elif args.op == 'name2cids':
    cids=pubchem_utils.Name2Cids(BASE_URL, args.name_query, args.verbose)
    for cid in cids: print('%d'%cid)

  elif args.op == 'aid2name':
    xmlstr=pubchem_utils.Aid2DescriptionXML(BASE_URL, args.aid_query, args.verbose)
    name, source = pubchem_utils.AssayXML2NameAndSource(xmlstr)
    print('%d:\n\tName: %s\n\tSource: %s'%(aid2name, name, source))

  elif args.op == 'assaydescribe':
    pubchem_utils.DescribeAssay(BASE_URL, args.aid_query, args.verbose)

  elif args.op == 'assaydescriptions':
    pubchem_utils.GetAssayDescriptions(BASE_URL, aids, fout, args.skip, args.nmax, args.verbose)

  elif args.op == 'assayresults':
    #Requires AIDs and SIDs.
    pubchem_utils.GetAssayResults_Screening2(BASE_URL, aids, ids, fout, args.skip, args.nmax, args.verbose)

  else:
    parser.error('ERROR: no operation specified.')

  if args.verbose:
    logging.info(("total elapsed time: %s"%(time_utils.NiceTime(time.time()-t0))))
