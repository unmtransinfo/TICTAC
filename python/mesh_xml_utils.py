#!/usr/bin/env python3
'''
	MeSH XML utility functions.

	Jeremy Yang
'''
#############################################################################
### MeSH XML
### Download: https://www.nlm.nih.gov/mesh/download_mesh.html
### Doc: https://www.nlm.nih.gov/mesh/xml_data_elements.html
###  
### <DescriptorRecord DescriptorClass="1">
### 1 = Topical Descriptor.
### 2 = Publication Types, for example, 'Review'.
### 3 = Check Tag, e.g., 'Male' (no tree number)
### 4 = Geographic Descriptor (Z category of tree number).
###  
### Category "C" : Diseases
### Category "F" : Psychiatry and Psychology
### Category "F03" : Mental Disorders
### Thus, include "C*" and "F03*" only.
### Terms can have multiple TreeNumbers; diseases can be in non-disease cateories,
### in addition to a disease category.
#############################################################################
import sys,os,re,getopt,codecs,gzip

try:
  import xml.etree.cElementTree as ElementTree
except ImportError:
  import xml.etree.ElementTree

from xml.parsers import expat

BRANCHES={
	'A':'Anatomy',
	'B':'Organisms',
	'C':'Diseases',
	'D':'Chemicals and Drugs',
	'E':'Analytical, Diagnostic and Therapeutic Techniques, and Equipment',
	'F':'Psychiatry and Psychology',
	'G':'Phenomena and Processes',
	'H':'Disciplines and Occupations',
	'I':'Anthropology, Education, Sociology, and Social Phenomena',
	'J':'Technology, Industry, and Agriculture',
	'K':'Humanities',
	'L':'Information Science',
	'M':'Named Groups',
	'N':'Health Care',
	'V':'Publication Characteristics',
	'Z':'Geographicals'}

#############################################################################
def Desc2Csv(branch, fin, fout, verbose):
  fout.write('id\ttreenum\tterm\n')
  n_elem=0; n_term=0;
  for event, elem in ElementTree.iterparse(fin):
    meshid,meshterm,desclass,treenum = None,None,None,None;
    n_elem+=1
    if verbose>2: print('DEBUG: event:%6s, elem.tag:%6s, elem.text:"%6s"'%(event,elem.tag,elem.text.strip() if elem.text else ''),file=sys.stderr)
    if elem.tag == 'DescriptorRecord':
      if elem.attrib['DescriptorClass'] != '1': continue
      meshid,meshterm,desclass,treenum = None,None,None,None;
      meshid=elem.findtext('DescriptorUI')
      #treenum=elem.findtext('TreeNumberList/TreeNumber')
      elems = elem.findall('TreeNumberList/TreeNumber')
      treenums = map(lambda e: e.text, elems)
      for treenum in treenums:
        if (re.match(r'^%s'%branch,treenum)): break
      meshterm=elem.findtext('DescriptorName/String')
      #See also: ConceptList/Concept/TermList/Term/String (may be multiple)

      if not meshid:
        if verbose>1:
          print('skipping, no meshid: %s'%str(elem), file=sys.stderr)
      elif not meshterm:
        if verbose>1:
          print('meshid: %s ; skipping, no meshterm'%meshid, file=sys.stderr)
      elif not treenum:
        if verbose>1:
          print('meshid: %s ; skipping, no treenum'%meshid, file=sys.stderr)
      elif not re.match(r'^%s'%branch,treenum):
        if verbose>1:
          print('meshid: %s ; skipping, non-%s treenum: %s'%(meshid,branch,treenum), file=sys.stderr)
      else:
        fout.write('%s\t%s\t%s\n'%(meshid,treenum,meshterm))
        n_term+=1

  print('DEBUG: n_elem: %d'%n_elem,file=sys.stderr)
  print('DEBUG: n_term: %d'%n_term,file=sys.stderr)

#############################################################################
### SCRClass
### Description: Attribute of <DescriptorRecord> one of:
### 1 = Regular chemical, drug, or other substance (the most common type)
### 2 = Protocol, for example, FOLFOXIRI protocol
### 3 = Rare disease, for example, Canicola fever
### Subelement of: not applicable. Attribute of <SupplementalRecord>
### Record Type: SCR
### https://www.nlm.nih.gov/mesh/xml_data_elements.html
#############################################################################
### There are non-disease records mapped to diseases, e.g. C041229,
### "GHM protein, human", SCRClass=1, is mapped to D006362, "Heavy Chain Disease".
### These cannot be identified from the supplementary file alone.
#############################################################################
def Supp2Csv(branch, fin, fout, verbose):
  fout.write('id\tterm\tid_to\tterm_to\n')
  n_elem=0; n_term=0;
  for event,elem in ElementTree.iterparse(fin):
    meshid,name,meshid_to,meshterm_to = None,None,None,None;
    n_elem+=1
    if verbose>2: print('DEBUG: event:%6s, elem.tag:%6s, elem.text:"%6s"'%(event,elem.tag,elem.text.strip() if elem.text else ''),file=sys.stderr)
    if elem.tag == 'SupplementalRecord':
      scrclass = elem.attrib['SCRClass']
      if branch not in ('C', 'D'): continue
      if branch=='C' and scrclass!='3': continue #disease-only
      if branch=='D' and scrclass!='1': continue #chemical-only
      meshid=elem.findtext('SupplementalRecordUI')
      name=elem.findtext('SupplementalRecordName/String')
      mtlist=elem.find('HeadingMappedToList')
      if mtlist is None:
        continue
      meshid_to=mtlist.findtext('HeadingMappedTo/DescriptorReferredTo/DescriptorUI')
      meshterm_to=mtlist.findtext('HeadingMappedTo/DescriptorReferredTo/DescriptorName/String')
      fout.write('%s\t%s\t%s\t%s\n'%(meshid,name,meshid_to,meshterm_to))
      n_term+=1
  #print('DEBUG: n_elem: %d'%n_elem, file=sys.stderr)
  print('n_term: %d'%n_term, file=sys.stderr)

#############################################################################
if __name__=='__main__':
  PROG=os.path.basename(sys.argv[0])
  branch='C'
  def ErrorExit(msg):
    print(msg)
    sys.exit(1)
  usage='''
%(PROG)s - MeSH XML utility

required:
  --i IFILE ............ input MeSH XML file [stdin]

operations:
  --desc2csv ............ descriptors XML input
  --supp2csv ............ supplementary records XML input

options:
  --o OFILE ............ output file
  --branch BRANCH ...... top-level branch of MeSH tree [%(BRANCH)s]
  --force .............. ignore UTF-8 encoding errors
  --v[v] ............... verbose [very]
  --h .................. help

Branches:
	%(BRANCHLIST)s
'''%{	'PROG':PROG,
	'BRANCH':branch,
	'BRANCHLIST':('\n\t'.join(['%s: %s'%(k,BRANCHES[k]) for k in sorted(BRANCHES.keys())]))
	}
  ifile=None; ofile=None;
  desc2csv=False; 
  supp2csv=False; 
  force=False;
  verbose=0;
  opts,pargs = getopt.getopt(sys.argv[1:],'',['h','v','vv','i=','o=','branch=',
	'force', 'desc2csv', 'supp2csv'  ])
  if not opts: ErrorExit(usage)
  for (opt,val) in opts:
    if opt=='--h': ErrorExit(usage)
    elif opt=='--i': ifile=val
    elif opt=='--o': ofile=val
    elif opt=='--branch': branch=val
    elif opt=='--desc2csv': desc2csv=True
    elif opt=='--supp2csv': supp2csv=True
    elif opt=='--force': force=True
    elif opt=='--vvv': verbose=3
    elif opt=='--vv': verbose=2
    elif opt=='--v': verbose=1
    else: ErrorExit('Illegal option: %s'%val)

  codecs_mode = "ignore" if force else "replace"
  root=None
  if ifile:
    fin=codecs.open(ifile,"r","UTF-8",codecs_mode)
    if not fin: ErrorExit('ERROR: failed to open: %s'%ifile)
  else:
    fin=codecs.getreader("UTF-8")(sys.stdin)

  if ofile:
    fout=codecs.open(ofile,"w","UTF-8",codecs_mode)
    if not fout: ErrorExit('ERROR: cannot open outfile: %s'%ofile)
  else:
    fout=codecs.getwriter("UTF-8")(sys.stdout,errors=codecs_mode)

  if branch not in BRANCHES:
    ErrorExit('ERROR: invalid branch: %s'%branch)

  if desc2csv:
    Desc2Csv(branch, fin, fout, verbose)
    fout.close()

  elif supp2csv:
    Supp2Csv(branch, fin, fout, verbose)
    fout.close()

  else:
    ErrorExit('No operation specified.')
