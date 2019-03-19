#!/usr/bin/env python3
#############################################################################
### See https://github.com/chembl/chembl_webresource_client
#############################################################################
import sys,os,argparse,csv
from chembl_webresource_client.new_client import new_client

nchunk = 50

#############################################################################
### Compounds to targets through activities.
### ChEMBL target IDs to uniprot IDs.
### Process in chunks to avoid timeouts due to size.
#############################################################################
### Currently ONLY activities with pChembl values for quality assurance.
#############################################################################
### Activity fields:
#	activity_comment, activity_id, assay_chembl_id, assay_description, assay_type,
#	bao_endpoint, bao_format, bao_label, canonical_smiles, data_validity_comment,
#	data_validity_description, document_chembl_id, document_journal,
#	document_year, ligand_efficiency, molecule_chembl_id, molecule_pref_name,
#	parent_molecule_chembl_id, pchembl_value, potential_duplicate, published_relation,
#	published_type, published_units, published_value, qudt_units, record_id, relation,
#	src_id, standard_flag, standard_relation, standard_text_value, standard_type,
#	standard_units, standard_upper_value, standard_value, target_chembl_id, 
#	target_organism, target_pref_name, target_tax_id, text_value, toid, type, 
#	units, uo_units, upper_value, value
#############################################################################
act_tags_selected = [
	'activity_id',
	'assay_chembl_id', 'assay_type', 'src_id',
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
  nact=0;
  with open(ofile, 'w') as csvfile:
    writer = csv.writer(csvfile, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
    for i in range(0, len(cids), nchunk):
      #print('DEBUG: Request IDs: %s'%(','.join(cids[i:i + nchunk])), file=sys.stderr)
      acts = new_client.activity.filter(molecule_chembl_id__in=cids[i:i+nchunk]).only(act_tags_selected)
      for act in acts:
        if not tags:
          tags = list(act.keys())
          writer.writerow(tags)
        if ('pchembl_value' not in act) or not act['pchembl_value']:
          continue
        writer.writerow([(act[tag] if tag in act else '') for tag in tags])
        nact+=1
  print('Output activities (with pchembl): %d'%nact, file=sys.stderr)

#############################################################################
### Need to include some target fields.
### Target fields:
### 'cross_references', 'organism', 'pref_name', 'species_group_flag',
### 'target_chembl_id', 'target_components', 'target_type', 'tax_id'
#############################################################################
def TID2Targetcomponents(ifile, ofile, verbose):
  tids = []
  t_tags=['target_chembl_id','target_type','organism', 'species_group_flag',
	'tax_id']
  tc_tags=['component_id','component_type','component_description','relationship',
	'accession']
  with open(ifile, 'r') as csvfile:
    reader = csv.reader(csvfile, delimiter='\t')
    for row in reader:
      tids.append(row[0])
  print('Input TIDs: %d'%len(tids), file=sys.stderr)
  ntc=0;
  with open(ofile, 'w') as csvfile:
    writer = csv.writer(csvfile, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
    for i in range(0, len(tids), nchunk):
      targets = new_client.target.filter(target_chembl_id__in=tids[i:i+nchunk])
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
    for i in range(0, len(dids), nchunk):
      documents = new_client.document.filter(document_chembl_id__in=dids[i:i+nchunk])
      for d in documents:
        #print('DEBUG: document tags: %s'%(str(d.keys())), file=sys.stderr)
        #print('DEBUG: document: %s'%(str(d)), file=sys.stderr)
        d_vals=[(d[tag] if tag in d else '') for tag in d_tags]
        writer.writerow(d_vals)
        ndoc+=1
  print('Output documents: %d'%ndoc, file=sys.stderr)

#############################################################################
if __name__=='__main__':

  parser = argparse.ArgumentParser(
        description='ChEMBL REST API client: lookup data by IDs')
  ops = ['cid2Activity', 'tid2Targetcomponents','did2Documents']
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
  elif args.op == 'tid2Targetcomponents':
    TID2Targetcomponents(args.ifile, args.ofile, args.verbose)
  elif args.op == 'did2Documents':
    DID2Documents(args.ifile, args.ofile, args.verbose)
 
