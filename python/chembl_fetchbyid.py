#!/usr/bin/env python3
#############################################################################
### See https://github.com/chembl/chembl_webresource_client
#############################################################################
### Not all fields included. Lists/dicts excluded.
#############################################################################
import sys,os,argparse,csv
from chembl_webresource_client.new_client import new_client

NCHUNK = 50

#############################################################################
### Compounds to targets through activities.
### ChEMBL target IDs to uniprot IDs.
### Process in chunks to avoid timeouts due to size.
#############################################################################
### Currently ONLY activities with pChembl values for quality assurance.
#############################################################################
act_tags_selected = ['activity_id', 'assay_chembl_id', 'assay_type', 'src_id',
	'relation', 'standard_relation',
	'target_chembl_id', 'target_pref_name', 'target_organism', 'target_tax_id',
	'molecule_chembl_id', 'parent_molecule_chembl_id', 'molecule_pref_name',
	'document_chembl_id', 'document_year',
	'pchembl_value', 'value', 'standard_value',
	'text_value', 'published_value',
	'units', 'qudt_units', 'uo_units', 'published_units', 'standard_units',
	'type', 'published_type', 'standard_type']
#
def CID2Activity(ifile, ofile, verbose):
  cids = []
  with open(ifile, 'r') as csvfile:
    reader = csv.reader(csvfile, delimiter='\t')
    for row in reader:
      cids.append(row[0])
  print('Input CIDs: %d'%len(cids), file=sys.stderr)
  tags=None;
  n_act=0;
  with open(ofile, 'w') as csvfile:
    writer = csv.writer(csvfile, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
    for i in range(0, len(cids), NCHUNK):
      #print('DEBUG: Request IDs: %s'%(','.join(cids[i:i + NCHUNK])), file=sys.stderr)
      acts = new_client.activity.filter(molecule_chembl_id__in=cids[i:i+NCHUNK]).only(act_tags_selected)
      for act in acts:
        if not tags:
          tags = list(act.keys())
          writer.writerow(tags)
        if ('pchembl_value' not in act) or not act['pchembl_value']:
          continue
        writer.writerow([(act[tag] if tag in act else '') for tag in tags])
        n_act+=1
      if verbose:
        print('Progress: %d / %d ; activities: %d'%(i, len(cids), n_act), file=sys.stderr)
  print('Output activities (with pchembl): %d'%n_act, file=sys.stderr)

#############################################################################
def TID2Targetcomponents(ifile, ofile, verbose):
  tids = []
  t_tags=['target_chembl_id','target_type','organism', 'species_group_flag', 'tax_id']
  tc_tags=['component_id','component_type','component_description','relationship', 'accession']
  with open(ifile, 'r') as csvfile:
    reader = csv.reader(csvfile, delimiter='\t')
    for row in reader:
      tids.append(row[0])
  print('Input TIDs: %d'%len(tids), file=sys.stderr)
  ntc=0;
  with open(ofile, 'w') as csvfile:
    writer = csv.writer(csvfile, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
    for i in range(0, len(tids), NCHUNK):
      targets = new_client.target.filter(target_chembl_id__in=tids[i:i+NCHUNK])
      for t in targets:
        #print('DEBUG: target tags: %s'%(str(t.keys())), file=sys.stderr)
        #print('DEBUG: target: %s'%(str(t)), file=sys.stderr)
        t_vals=[(t[tag] if tag in t else '') for tag in t_tags]
        for tc in t['target_components']:
          if tc['component_type'] != 'PROTEIN':
            continue
          if ntc==0:
            writer.writerow(t_tags+tc_tags)
          tc_vals=[(tc[tag] if tag in tc else '') for tag in tc_tags]
          writer.writerow(t_vals+tc_vals)
          ntc+=1
  print('Output target components (PROTEIN): %d'%ntc, file=sys.stderr)

#############################################################################
def DID2Documents(ifile, ofile, verbose):
  dids = []
  d_tags=['document_chembl_id', 'doc_type', 'src_id', 'pubmed_id',
	'patent_id', 'doi', 'doi_chembl', 'year', 'journal', 'authors',
	'volume', 'issue', 'title', 'journal_full_title', 'abstract']
  with open(ifile, 'r') as csvfile:
    reader = csv.reader(csvfile, delimiter='\t')
    for row in reader:
      dids.append(row[0])
  print('Input DIDs: %d'%len(dids), file=sys.stderr)
  ndoc=0;
  with open(ofile, 'w') as csvfile:
    writer = csv.writer(csvfile, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
    for i in range(0, len(dids), NCHUNK):
      documents = new_client.document.filter(document_chembl_id__in=dids[i:i+NCHUNK])
      for d in documents:
        #print('DEBUG: document tags: %s'%(str(d.keys())), file=sys.stderr)
        #print('DEBUG: document: %s'%(str(d)), file=sys.stderr)
        d_vals=[(d[tag] if tag in d else '') for tag in d_tags]
        if ndoc==0:
          writer.writerow(d_tags)
        writer.writerow(d_vals)
        ndoc+=1
  print('Output documents: %d'%ndoc, file=sys.stderr)

#############################################################################
def InchiKey2Molecule(ifile, ofile, verbose):
  inkeys = []
  m_tags=[
	'availability_type', 'biotherapeutic', 'black_box_warning', 'chebi_par_id', 
	'chirality', 'dosed_ingredient', 'first_approval', 'first_in_class', 
	'helm_notation', 'indication_class', 'inorganic_flag', 'max_phase', 
	'molecule_chembl_id', 'molecule_type', 'natural_product', 'oral', 
	'parenteral', 'polymer_flag', 'pref_name', 'prodrug', 'structure_type', 
	'therapeutic_flag', 'topical', 'usan_stem', 'usan_stem_definition', 
	'usan_substem', 'usan_year', 'withdrawn_class', 'withdrawn_country', 
	'withdrawn_flag', 'withdrawn_reason', 'withdrawn_year']
  with open(ifile, 'r') as csvfile:
    reader = csv.reader(csvfile, delimiter='\t')
    for row in reader:
      inkeys.append(row[0])
  print('Input inchikeys: %d'%len(inkeys), file=sys.stderr)
  n_mol=0;
  with open(ofile, 'w') as csvfile:
    writer = csv.writer(csvfile, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
    for i in range(0, len(inkeys), NCHUNK):
      mol = new_client.molecule
      mols = mol.get(inkeys[i:i+NCHUNK])
      for ii,m in enumerate(mols):
        inkey = inkeys[i+ii]
        #print('DEBUG: mol tags: %s'%(str(m.keys())), file=sys.stderr)
        #print('DEBUG: mol: %s'%(str(m)), file=sys.stderr)
        m_vals=[inkey]+[(m[tag] if tag in m else '') for tag in m_tags]
        if n_mol==0:
          writer.writerow(['inchikey']+m_tags)
        writer.writerow(m_vals)
        n_mol+=1
  print('Output mols: %d'%n_mol, file=sys.stderr)

#############################################################################
if __name__=='__main__':

  parser = argparse.ArgumentParser(
        description='ChEMBL REST API client: lookup data by IDs')
  ops = ['cid2Activity', 'tid2Targetcomponents','did2Documents', 'inchikey2Mol']
  parser.add_argument("op",choices=ops,help='operation')
  parser.add_argument("--i",dest="ifile",help="input file, IDs")
  parser.add_argument("--o",dest="ofile",help="output (CSV)")
  parser.add_argument("-v","--verbose",action="count")
  args = parser.parse_args()

  if not args.ifile:
    parser.error('Input file required.')
  if not args.ofile:
    parser.error('Output file required.')

  if args.op == 'cid2Activity':
    CID2Activity(args.ifile, args.ofile, args.verbose)
  elif args.op == 'inchikey2Mol':
    InchiKey2Molecule(args.ifile, args.ofile, args.verbose)
  elif args.op == 'tid2Targetcomponents':
    TID2Targetcomponents(args.ifile, args.ofile, args.verbose)
  elif args.op == 'did2Documents':
    DID2Documents(args.ifile, args.ofile, args.verbose)
 
