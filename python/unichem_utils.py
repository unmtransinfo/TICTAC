#!/usr/bin/env python3
"""
	Command line utility for UniChem REST API.
	Using both methods:
	(1) Python package:
	https://github.com/chembl/chembl_webresource_client.
	(2) REST API directly:
	https://www.ebi.ac.uk/unichem/info/webservices

Help on module chembl_webresource_client.unichem in chembl_webresource_client:

NAME
    chembl_webresource_client.unichem

CLASSES
    builtins.object
        UniChemClient
    
    class UniChemClient(builtins.object)
     |  Methods defined here:
     |  
     |  __init__(self)
     |      Initialize self.  See help(type(self)) for accurate signature.
     |  
     |  connectivity(self, pk, src_id=None, **kwargs)
     |  
     |  get(self, pk, src_id=None, to_src_id=None, all=False, url=False, verbose=False)
     |  
     |  inchiFromKey(self, inchi_key)
     |  
     |  map(self, src, dst=None)
     |  
     |  src(self, pk=None)
     |  
     |  structure(self, pk, src, all=False)
"""
import sys,os,re,argparse,time,json
#
import rest_utils
#
PROG=os.path.basename(sys.argv[0])
#
API_HOST='www.ebi.ac.uk'
API_BASE_PATH='/unichem/rest'
#
# From https://www.ebi.ac.uk/unichem/ucquery/listSources (20190424)
SOURCES = {
1:{'short_name':'chembl', 'full_name':'ChEMBL'},
2:{'short_name':'drugbank', 'full_name':'DrugBank'},
3:{'short_name':'pdb', 'full_name':'PDBe (Protein Data Bank Europe)'},
4:{'short_name':'gtopdb', 'full_name':'Guide to Pharmacology'},
5:{'short_name':'pubchem_dotf', 'full_name':'PubChem ("Drugs of the Future" subset)'},
6:{'short_name':'kegg_ligand', 'full_name':'KEGG (Kyoto Encyclopedia of Genes and Genomes) Ligand'},
7:{'short_name':'chebi', 'full_name':'ChEBI (Chemical Entities of Biological Interest).'},
8:{'short_name':'nih_ncc', 'full_name':'NIH Clinical Collection'},
9:{'short_name':'zinc', 'full_name':'ZINC'},
10:{'short_name':'emolecules', 'full_name':'eMolecules'},
11:{'short_name':'ibm', 'full_name':'IBM strategic IP insight platform and the National Institutes of Health'},
12:{'short_name':'atlas', 'full_name':'Gene Expression Atlas'},
14:{'short_name':'fdasrs', 'full_name':'FDA/USP Substance Registration System (SRS)'},
15:{'short_name':'surechembl', 'full_name':'SureChEMBL'},
17:{'short_name':'pharmgkb', 'full_name':'PharmGKB'},
18:{'short_name':'hmdb', 'full_name':'Human Metabolome Database (HMDB)'},
20:{'short_name':'selleck', 'full_name':'Selleck'},
21:{'short_name':'pubchem_tpharma', 'full_name':'PubChem ("Thomson Pharma" subset)'},
22:{'short_name':'pubchem', 'full_name':'PubChem Compounds'},
23:{'short_name':'mcule', 'full_name':'Mcule'},
24:{'short_name':'nmrshiftdb2', 'full_name':'NMRShiftDB'},
25:{'short_name':'lincs', 'full_name':'Library of Integrated Network-based Cellular Signatures'},
26:{'short_name':'actor', 'full_name':'ACToR'},
27:{'short_name':'recon', 'full_name':'Recon'},
28:{'short_name':'molport', 'full_name':'MolPort'},
29:{'short_name':'nikkaji', 'full_name':'Nikkaji'},
31:{'short_name':'bindingdb', 'full_name':'BindingDB'},
32:{'short_name':'comptox', 'full_name':'EPA (Environmental Protection Agency) CompTox Dashboard'},
33:{'short_name':'lipidmaps', 'full_name':'LipidMaps'},
34:{'short_name':'drugcentral', 'full_name':'DrugCentral'},
35:{'short_name':'carotenoiddb', 'full_name':'Carotenoid Database'},
36:{'short_name':'metabolights', 'full_name':'Metabolights'},
37:{'short_name':'brenda', 'full_name':'Brenda'},
38:{'short_name':'rhea', 'full_name':'Rhea'},
39:{'short_name':'chemicalbook', 'full_name':'ChemicalBook'},
41:{'short_name':'swisslipids', 'full_name':'SwissLipids'}
}
#
##############################################################################
def GetMapping(ids,from_src,to_src,fout,verbose):
  fout.write('src_id_%s\tsrc_id_%s\n'%(from_src,to_src))
  for id_query in ids:
    n_qry+=1
    if verbose>1:
      print('query: "%s"'%id_query, file=sys.stderr)
    try:
      xrefs=unichem.get(id_query, src_id=from_src, to_src_id=to_src, verbose=verbose)
    except Exception as e:
      print('Not found: %s'%id_query, file=sys.stderr)
      continue
    if not xrefs or type(xrefs) is not list:
      print('Not found: %s'%id_query, file=sys.stderr)
      continue
    mols = rval
    ok=False
    hits_this=0
    for mol in mols:
      id_dst = mol['src_compound_id'] if 'src_compound_id' in mol else ''
      if id_dst:
        ok=True
        hits_this+=1
      fout.write('%s\t%s\n'%(id_query,id_dst))
      n_out+=1
    if not ok:
      n_unmapped+=1
    if hits_this>1:
      n_ambig+=1

  print('n_qry: %d'%(n_qry), file=sys.stderr)
  print('n_unmapped: %d'%(n_unmapped), file=sys.stderr)
  print('n_ambig: %d'%(n_ambig), file=sys.stderr)
  print('n_out: %d'%(n_out), file=sys.stderr)
  
##############################################################################
def GetStructure(ids,src_id,fout,verbose):
  n_qry=0; n_unmapped=0; n_ambig=0; n_out=0; 
  tags=None;
  for id_query in ids:
    n_qry+=1
    if verbose>1:
      print('query: "%s"'%id_query, file=sys.stderr)
    try:
      mols = unichem.structure(id_qry, src=src_id, all=True)
    except Exception as e:
      print('Not found: %s'%id_query, file=sys.stderr)
      continue
    ok=False
    hits_this=0
    for mol in mols:
      if n_out==0 or not tags:
        tags = mol.keys()
        fout.write('\t'.join(tags)+'\n')
      vals = [str(id_query)]
      for tag in tags:
        vals.append(str(mol[tag]) if tag in mol else '')
      fout.write('\t'.join(vals)+'\n')
      n_out+=1
  print('n_qry: %d'%(n_qry), file=sys.stderr)
  print('n_out: %d'%(n_out), file=sys.stderr)

##############################################################################
def GetByInchikeys(inchikeys, fout, verbose):
  n_qry=0; n_out=0;
  fout.write('inchikey\tchembl_id\n')
  for inchikey in inchikeys:
    n_qry+=1
    rval=None; chemb_id='';
    inchikey = re.sub(r'^InChIKey=','',inchikey)
    if verbose>1:
      print('query: "%s"'%inchikey, file=sys.stderr)
    try:
      xrefs=unichem.get(inchikey)
    except Exception as e:
      print('Not found: %s'%inchikey, file=sys.stderr)
      continue
    if not xrefs or type(xrefs) is not list:
      print('Not found: %s'%inchikey, file=sys.stderr)
      continue
    chembl_id = None
    for xref in xrefs:
      if 'src_id' in xref and xref['src_id']=='1':
        chembl_id = xref['src_compound_id'] if 'src_compound_id' in xref else ''
    if chembl_id:
      fout.write('%s\t%s\n'%(inchikey,chembl_id))
      n_out+=1
  print('n_qry: %d'%(n_qry), file=sys.stderr)
  print('n_out: %d'%(n_out), file=sys.stderr)

#############################################################################
def ListSources(base_url, verbose):
  rval=rest_utils.GetURL(base_url+'/src_ids',parse_json=True,verbose=verbose)
  src_ids=[]
  for s in rval:
    if 'src_id' in s:
      src_ids.append(int(s['src_id']))
  for src_id in src_ids:
    info = GetSourceInfo(base_url,src_id,verbose)
    name = info['name'] if 'name' in info else ''
    name_label = info['name_label'] if 'name_label' in info else ''
    name_long = info['name_long'] if 'name_long' in info else ''
    print('%2d: %s (%s)'%(src_id,name_label,name_long))
    if verbose>2:
      for key in sorted(info.keys()):
        print('\t%14s: %s'%(key,info[key]))
  print('source count: %d'%len(src_ids), file=sys.stderr)

##############################################################################
def GetSourceInfo(base_url, src_id, verbose):
  rval=rest_utils.GetURL(base_url+'/sources/%s'%src_id,parse_json=True,verbose=verbose)
  if verbose>2: print(json.dumps(rval,sort_keys=True,indent=2), file=sys.stderr)
  info = rval[0] if (rval and len(rval)==1) else {}
  return info

#############################################################################
if __name__=='__main__':

  parser = argparse.ArgumentParser(
        description='UniChem REST API client')
  ops = ['get_mapping', 'get_by_inchikey', 'get_structure', 'listSources']
  parser.add_argument("op", choices=ops, help='operation')
  parser.add_argument("--i", dest="ifile", help="input file, IDs")
  parser.add_argument("--id", help="input IDs")
  parser.add_argument("--o", dest="ofile", help="output (CSV)")
  parser.add_argument("--from_src", type=int, help='from-source ID code (required for --get)')
  parser.add_argument("--to_src", type=int, help='to-source ID code (required for --get)')
  parser.add_argument("--skip", type=int)
  parser.add_argument("--nmax", type=int)
  parser.add_argument("--api_host", default=API_HOST)
  parser.add_argument("--api_base_path", default=API_BASE_PATH)
  parser.add_argument("-v","--verbose", default=0, action="count")
  args = parser.parse_args()

  API_BASE_URL='https://'+args.api_host+args.api_base_path

  if args.op=='listSources':
    #print('%6s:%18s (%s)'%('src_id', 'short_name', 'full_name'))
    #for src_id in sorted(SOURCES.keys()):
    #  print('%6s:%18s (%s)'%(src_id, SOURCES[src_id]['short_name'], SOURCES[src_id]['full_name']))
    ListSources(API_BASE_URL, args.verbose)
    sys.exit()

  if not (args.ifile or args.id):
    parser.error('--i or --id required.')

  if args.ofile:
    fout = open(args.ofile, 'w')
  else:
    fout = sys.stdout

  if args.ofile:
    fout=open(ofile, "w")
  else:
    fout=sys.stdout

  ids=[]
  if args.ifile:
    fin=open(args.ifile)
    if not fin: parser.error('Cannot open: %s'%args.ifile)
    while True:
      line=fin.readline()
      if not line: break
      ids.append(line.rstrip())
    if verbose:
      print('input IDs: %d'%(len(ids)), file=sys.stderr)
    fin.close()
  elif args.id:
    ids.append(args.id)

  #unichem_client instance of UniChemClient
  from chembl_webresource_client.unichem import unichem_client as unichem

  if args.op=='get_mapping':
    if not ids: parser.error('--id or --i required.')
    if not (args.from_src and args.to_src): parser.error('--from_src and --to_src required.')
    GetMapping(ids, args.from_src, args.to_src, fout, args.verbose)

  elif args.op=='get_structure':
    if not ids: parser.error('--id or --i required.')
    if not args.from_src: parser.error('--from_src required.')
    GetStructure(ids, args.from_src, fout, args.verbose)

  elif args.op=='get_by_inchikey':
    if not ids: parser.error('--id or --i required.')
    GetByInchikeys(ids, fout, args.verbose)

  else:
    parser.error('No operation specified.')
