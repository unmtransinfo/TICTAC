#!/usr/bin/env python
##############################################################################
### pubchem_utils.py - utility functions for the PubChem PUG REST API.
###
### see: http://pubchem.ncbi.nlm.nih.gov/rest/pug/
### URL paths:
###	<domain>/<namespace>/<identifiers>
###
###  compound domain:
###	compound/cid 
### 	compound/name 
### 	compound/smiles 
### 	compound/inchi 
### 	compound/inchikey 
### 	compound/listkey
### 	compound/substructure/{smiles|inchi}
###
###  substance domain:
###	substance/sid 
### 	substance/name 
### 	substance/listkey
### 	substance/sourceid/<source name> 
### 	substance/sourceall/<source name> 
###     substance/sid/<SID>/cids/JSON
###     substance/sid/<SID>/cids/XML?cids_type=all
###
###  assay domain:
###	assay/aid 
### 	assay/listkey 
### 	assay/type/{all|confirmatory|doseresponse|onhold|panel|rnai|screening|summary}
### 	assay/sourceall/<source name>
###
###  sources domain:
###	sources/{substance|assay}
###
###  <identifiers> = comma-separated list of positive integers (cid, sid, aid) or
###  identifier strings (source, inchikey, listkey); single identifier string
###  (name, smiles; inchi by POST only)
##############################################################################
import sys,os,re,types,math,time
import urllib,urllib2
import csv,json
import xml.dom.minidom #replace with ETree
#
import rest_utils
import time_utils
#
OFMTS={
	'XML':'application/xml',
	'JSON':'application/json',
	'JSONP':'application/javascript',
	'ASNB':'application/ber-encoded',
	'SDF':'application/x-mdl-sdfile',
	'CSV':'text/csv',
	'PNG':'image/png',
	'TXT':'text/plain'
	}
#
OUTCOME_CODES = {'inactive':1,'active':2,'inconclusive':3,'unspecified':4,'probe':5}
#
#############################################################################
def ListSubstanceSources(base_url,fout,verbose):
  rval=rest_utils.GetURL(base_url+'/sources/substance/JSON',parse_json=True,verbose=verbose)
  #print >>sys.stderr, json.dumps(rval,indent=2)
  sources = rval['InformationList']['SourceName']
  n_src=0;
  for source in sorted(sources):
    fout.write('"%s"\n'%source)
    n_src+=1
  print >>sys.stderr, 'n_src: %d'%n_src
  return

#############################################################################
def ListAssaySources(base_url,fout,verbose):
  rval=rest_utils.GetURL(base_url+'/sources/assay/JSON',parse_json=True,verbose=verbose)
  #print >>sys.stderr, json.dumps(rval,indent=2)
  sources = rval['InformationList']['SourceName']
  n_src=0;
  for source in sorted(sources):
    fout.write('"%s"\n'%source)
    n_src+=1
  print >>sys.stderr, 'n_src: %d'%n_src
  return

##############################################################################
def Cid2Sdf(base_url,id_query,verbose=0):
  url=(base_url+'/compound/cid/%d/SDF'%id_query)
  if verbose>2: print >>sys.stderr, 'URL: %s'%url
  txt=rest_utils.GetURL(url,verbose=verbose)
  return txt

#############################################################################
def Cid2Smiles(base_url,id_query,verbose=0):
  url=(base_url+'/compound/cid/%d/property/IsomericSMILES/JSON'%id_query)
  if verbose>2: print >>sys.stderr, 'URL: %s'%url
  d=rest_utils.GetURL(url,parse_json=True,verbose=verbose)
  try:
    props = d['PropertyTable']['Properties']
    smi=props[0]['IsomericSMILES']
  except Exception, e:
    print >>sys.stderr, 'Error (Exception): %s'%e
    #print >>sys.stderr, 'DEBUG: d = %s'%str(d)
    smi=None
  return smi

##############################################################################
def Sid2Sdf(base_url,id_query,verbose=0):
  url=(base_url+'/substance/sid/%d/SDF'%id_query)
  if verbose>2: print >>sys.stderr, 'URL: %s'%url
  #txt=rest_utils.GetURL(url,headers={'Accept':'%s'%OFMTS['TXT']},verbose=verbose)
  txt=rest_utils.GetURL(url,verbose=verbose)
  return txt

#############################################################################
def Sid2AssaySummaryCSV(base_url,id_query,verbose=0):
  txt=rest_utils.GetURL(base_url+'/substance/sid/%d/assaysummary/CSV'%id_query,verbose=verbose)
  #print >>sys.stderr, 'DEBUG: 1st line: %s'%txt.splitlines()[0]
  return txt

#############################################################################
def Sid2Cid(base_url,sid,verbose=0):
  d=rest_utils.GetURL(base_url+'/substance/sid/%d/cids/JSON?cids_type=standardized'%sid,parse_json=True,verbose=verbose)
  try:
    infos = d['InformationList']['Information']
    cid=infos[0]['CID'][0]
  except Exception, e:
    print >>sys.stderr, 'Error (Exception): %s'%e
    #print >>sys.stderr, 'DEBUG: d = %s'%str(d)
    cid=None
  #print >>sys.stderr, 'DEBUG: sid=%s ; cid=%s'%(sid,cid)
  return cid

#############################################################################
def Sid2Smiles(base_url,sid,verbose=0):
  cid = Sid2Cid(base_url,sid,verbose)
  return Cid2Smiles(base_url,cid,verbose)

#############################################################################
def Cid2Sids(base_url,cid,verbose=0):
  d=rest_utils.GetURL(base_url+'/compound/cid/%d/sids/JSON'%cid,parse_json=True,verbose=verbose)
  sids=[]
  try:
    infos = d['InformationList']['Information']
    for info in infos:
      sids.extend(info['SID'])
  except Exception, e:
    print >>sys.stderr, 'Error (Exception): %s'%e
    #print >>sys.stderr, 'DEBUG: d = %s'%str(d)
  return sids

#############################################################################
### JSON returned: "{u'IdentifierList': {u'CID': [245086]}}"
### Problem: must quote forward slash '/' in smiles.  2nd param in quote()
### specifies "safe" chars to not quote, '/' being the default, so specify
### '' for no safe chars.
#############################################################################
def Smi2Ids(base_url,smi,verbose):
  d=rest_utils.GetURL(base_url+'/compound/smiles/%s/cids/JSON'%urllib2.quote(smi,''),parse_json=True,verbose=verbose)
  if d and d.has_key('IdentifierList'):
    return d['IdentifierList']
  else:
    return None

#############################################################################
def Smi2Cids(base_url,smi,verbose):
  ids = Smi2Ids(base_url,smi,verbose)
  if ids and ids.has_key('CID'):
    return ids['CID']
  else:
    return []

#############################################################################
#  sids: '846753,846754,846755,846760,846761,3712736,3712737'
#  cids: '644415,5767160,644417,644418,644420'
#  Very slow -- progress?
#############################################################################
def Sids2Cids(base_url,ids,verbose=0):
  ## Use method POST; put SIDs in data.
  ids_txt='sid='+(','.join(map(lambda x:str(x),ids)))
  #print >>sys.stderr, 'DEBUG: ids_txt = %s'%ids_txt
  req=urllib2.Request(url=base_url+'/substance/sid/cids/TXT?cids_type=standardized',
	headers={'Accept':OFMTS['TXT'],'Content-type':'application/x-www-form-urlencoded'},
	data=ids_txt
	)
  #print >>sys.stderr, 'DEBUG: req.get_method() = %s'%req.get_method()
  #print >>sys.stderr, 'DEBUG: req.has_data() = %s'%req.has_data()
  f=urllib2.urlopen(req)
  cids=[]
  while True:
    line=f.readline()
    if not line: break
    try:
      cid=int(line)
      cids.append(cid)
    except:
      pass
  return cids

#############################################################################
def Sids2CidsCSV(base_url,ids,fout,verbose=0):
  t0 = time.time()
  fout.write('sid,cid\n')
  n_in=0; n_out=0; n_err=0;
  for sid in ids:
    n_in+=1
    cid = Sid2Cid(base_url,sid,verbose)
    try:
      cid=int(cid)
    except Exception, e:
      n_err+=1
      continue
    fout.write('%d,%d\n'%(sid,cid))
    n_out+=1
    if verbose>0 and (n_in%1000)==0:
      print >>sys.stderr, 'processed: %6d / %6d (%.1f%%); elapsed time: %s'%(n_in,len(ids), 100.0*n_in/len(ids),time_utils.NiceTime(time.time()-t0))
  print >>sys.stderr, 'sids in: %d'%len(ids)
  print >>sys.stderr, 'cids out: %d'%n_out
  print >>sys.stderr, 'errors: %d'%n_err

#############################################################################
def Cids2SidsCSV(base_url,ids,fout,verbose=0):
  fout.write('cid,sid\n')
  n_out=0; n_err=0;
  for cid in ids:
    try:
      d=rest_utils.GetURL(base_url+'/compound/cid/%s/sids/TXT'%cid,verbose=verbose)
      sids=d.splitlines()
    except Exception, e:
      print >>sys.stderr, 'Error (Exception): %s'%e
      n_err+=1
      continue
      #print >>sys.stderr, 'DEBUG: d = %s'%str(d)
    for sid in sids:
      fout.write('%s,%s\n'%(cid,sid))
      n_out+=1
  print >>sys.stderr, 'cids in: %d'%len(ids)
  print >>sys.stderr, 'sids out: %d'%n_out
  print >>sys.stderr, 'errors: %d'%n_err

#############################################################################
def Cids2Assaysummary(base_url,ids,fout,verbose=0):
  n_out=0; n_err=0;
  for cid in ids:
    try:
      d=rest_utils.GetURL(base_url+'/compound/cid/%s/assaysummary/CSV'%cid,verbose=verbose)
      rows=d.splitlines()
    except Exception, e:
      print >>sys.stderr, 'Error (Exception): %s'%e
      n_err+=1
      continue
    for i,row in enumerate(rows):
      if i==0 and n_out>0: continue #1 header only
      fout.write('%s\n'%(row))
      n_out+=1
  print >>sys.stderr, 'cids in: %d'%len(ids)
  print >>sys.stderr, 'assay summaries out: %d'%n_out
  print >>sys.stderr, 'errors: %d'%n_err

#############################################################################
def Sids2Assaysummary(base_url,ids,fout,verbose=0):
  n_out=0; n_err=0;
  for sid in ids:
    try:
      d=rest_utils.GetURL(base_url+'/substance/sid/%s/assaysummary/CSV'%sid,verbose=verbose)
      rows=d.splitlines()
    except Exception, e:
      print >>sys.stderr, 'Error (Exception): %s'%e
      n_err+=1
      continue
    for i,row in enumerate(rows):
      if i==0 and n_out>0: continue #1 header only
      fout.write('%s\n'%(row))
      n_out+=1
  print >>sys.stderr, 'sids in: %d'%len(ids)
  print >>sys.stderr, 'assay summaries out: %d'%n_out
  print >>sys.stderr, 'errors: %d'%n_err

#############################################################################
def Cids2Properties(base_url,ids,fout,verbose):
  ## Use method POST; put CIDs in data.
  ids_txt='cid='+(','.join(map(lambda x:str(x),ids)))
  #print >>sys.stderr, 'DEBUG: ids_txt = %s'%ids_txt
  req=urllib2.Request(url=base_url+'/compound/cid/property/IsomericSMILES,MolecularFormula,MolecularWeight,XLogP,TPSA/CSV',
	headers={'Accept':OFMTS['CSV'],'Content-type':'application/x-www-form-urlencoded'},
	data=ids_txt)
  f=urllib2.urlopen(req)
  while True:
    line=f.readline()
    if not line: break
    fout.write(line)

#############################################################################
def Cids2Inchi(base_url,ids,fout,verbose):
  ## Use method POST; put CIDs in data.
  ids_txt='cid='+(','.join(map(lambda x:str(x),ids)))
  #print >>sys.stderr, 'DEBUG: ids_txt = %s'%ids_txt
  req=urllib2.Request(url=base_url+'/compound/cid/property/InChI,InChIKey/CSV',
	headers={'Accept':OFMTS['CSV'],'Content-type':'application/x-www-form-urlencoded'},
	data=ids_txt)
  f=urllib2.urlopen(req)
  while True:
    line=f.readline()
    if not line: break
    fout.write(line)

#############################################################################
### Request in chunks.  Works for 50, and not for 200 (seems to be a limit).
#############################################################################
def Cids2Sdf(base_url,ids,fout,verbose):
  nchunk=50; nskip_this=0;
  while True:
    if nskip_this>=len(ids): break
    idstr=(','.join(map(lambda x:str(x),ids[nskip_this:nskip_this+nchunk])))
    d={'cid':idstr}
    txt=rest_utils.PostURL(base_url+'/compound/cid/SDF',data=d,verbose=verbose)
    fout.write(txt)
    nskip_this+=nchunk
  return

#############################################################################
### Request in chunks.  Works for 50, and not for 200 (seems to be a limit).
#############################################################################
def Sids2Sdf(base_url,sids,fout,skip,nmax,verbose):
  n_sid_in=0; n_sdf_out=0;
  if verbose:
    if skip: print >>sys.stderr, 'skip: [1-%d]'%skip
  nchunk=50; nskip_this=skip;
  while True:
    if nskip_this>=len(sids): break
    nchunk=min(nchunk,nmax-(nskip_this-skip))
    n_sid_in+=nchunk
    idstr=(','.join(map(lambda x:str(x),sids[nskip_this:nskip_this+nchunk])))
    txt=rest_utils.PostURL(base_url+'/substance/sid/SDF',data={'sid':idstr},verbose=verbose)
    if txt:
      fout.write(txt)
      eof = re.compile(r'^\$\$\$\$',re.M)
      n_sdf_out_this = len(eof.findall(txt))
      n_sdf_out+=n_sdf_out_this

    nskip_this+=nchunk
    if nmax and (nskip_this-skip)>=nmax:
      print >>sys.stderr, 'NMAX limit reached: %d'%nmax
      break

  #print >>sys.stderr, 'sids in: %d ; sdfs out: %d'%(n_sid_in,n_sdf_out)

  return n_sid_in,n_sdf_out

#############################################################################
### Request returns CSV format CID,"SMILES" which must be fixed.
#############################################################################
def Cids2Smiles(base_url,ids,isomeric,fout,verbose):
  t0 = time.time()
  nchunk=50; nskip_this=0;
  n_in=0; n_out=0; n_err=0;
  while True:
    if nskip_this>=len(ids): break
    ids_this = ids[nskip_this:nskip_this+nchunk]
    n_in+=len(ids_this)
    idstr=(','.join(map(lambda x:str(x),ids_this)))
    d={'cid':idstr}
    prop = 'IsomericSMILES' if isomeric else 'CanonicalSMILES'
    txt=rest_utils.PostURL(base_url+'/compound/cid/property/%s/CSV'%prop,data=d,verbose=verbose)
    if not txt:
      n_err+=1
      break
    lines=txt.splitlines()
    for line in lines:
      cid,smi = re.split(',',line)
      if cid.upper()=='CID': continue #header
      try:
        cid=int(cid)
      except:
        continue
      smi=smi.replace('"','')
      fout.write('%s %d\n'%(smi,cid))
      n_out+=1
    nskip_this+=nchunk
    if verbose>0 and (n_in%1000)==0:
      print >>sys.stderr, 'processed: %6d / %6d (%.1f%%); elapsed time: %s'%(n_in,len(ids), 100.0*n_in/len(ids),time_utils.NiceTime(time.time()-t0))
  print >>sys.stderr, 'cids in: %d'%n_in
  print >>sys.stderr, 'smiles out: %d'%n_out
  print >>sys.stderr, 'errors: %d'%n_err
  return

#############################################################################
def Inchi2Cids(base_url,inchi,verbose):
  '''	Must be POST with "Content-Type: application/x-www-form-urlencoded"
	or "Content-Type: multipart/form-data" with the POST body formatted accordingly.
	See: http://pubchem.ncbi.nlm.nih.gov/pug_rest/PUG_REST.html and
	http://pubchem.ncbi.nlm.nih.gov/pug_rest/PUG_REST_Tutorial.html
  '''
  ofmt='TXT'
  #ofmt='XML'
  cid=None
  url="http://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/inchi/cids/%s"%ofmt ### URL ok?
  #body_data=('\n'.join(map(lambda x:urllib2.quote(x),inchis)))
  body_data=('inchi='+urllib2.quote(inchi))
  req=urllib2.Request(url=url,
	headers={'Content-Type':'application/x-www-form-urlencoded','Accept':OFMTS[ofmt]},
	data=body_data)
  if verbose>1:
    print >>sys.stderr, 'url="%s"; inchi="%s"'%(url,inchi)
  #print >>sys.stderr, 'DEBUG: req.get_type() = %s'%req.get_type()
  #print >>sys.stderr, 'DEBUG: req.get_method() = %s'%req.get_method()
  #print >>sys.stderr, 'DEBUG: req.get_host() = %s'%req.get_host()
  #print >>sys.stderr, 'DEBUG: req.get_full_url() = %s'%req.get_full_url()
  #print >>sys.stderr, 'DEBUG: req.header_items() = %s'%req.header_items()
  #print >>sys.stderr, 'DEBUG: req.get_data() = %s'%req.get_data()
  #
  f=urllib2.urlopen(req)
  
  cids=[]
  while True:
    line=f.readline()
    if not line: break
    try:
      cid=int(line)
      cids.append(cid)
    except:
      pass
  return cids

#############################################################################
def Aid2DescriptionXML(base_url,id_query,verbose=0):
  x=rest_utils.GetURL(base_url+'/assay/aid/%d/description/XML'%id_query,verbose=verbose)
  return x

#############################################################################
def GetAssayDescriptions(base_url,ids,fout,skip,nmax,verbose=0):
  import xpath
  fout.write('ID,Source,Name,Target,Date\n')
  adesc_xpath='/PC-AssayContainer/PC-AssaySubmit/PC-AssaySubmit_assay/PC-AssaySubmit_assay_descr/PC-AssayDescription'
  tag_name='PC-AssayDescription_name'
  tag_source='PC-DBTracking_name'
  tag_year='Date-std_year'
  tag_month='Date-std_month'
  tag_day='Date-std_day'
  tag_tgtname='PC-AssayTargetInfo_name'
  n_in=0; n_out=0;
  for aid in ids:
    n_in+=1
    if skip and n_in<skip: continue
    if nmax and n_out==nmax: break
    xmlstr=rest_utils.GetURL(base_url+'/assay/aid/%d/description/XML'%aid,verbose=verbose)
    dom=xml.dom.minidom.parseString(xmlstr)
    desc_nodes = xpath.find(adesc_xpath,dom)
    for desc_node in desc_nodes:
      name=xpath.findvalue('//%s'%tag_name,desc_node)
      source=xpath.findvalue('//%s'%tag_source,desc_node)
      year=xpath.findvalue('//%s'%tag_year,desc_node)
      month=xpath.findvalue('//%s'%tag_month,desc_node)
      day=xpath.findvalue('//%s'%tag_day,desc_node)
      ymd = (year+month+day) if (year and month and day) else ''
      tgtname=xpath.findvalue('//%s'%tag_tgtname,desc_node)
      fout.write('%d,"%s","%s","%s",%s\n'%(aid,source,name,(tgtname if tgtname else ''),ymd))
      n_out+=1

#############################################################################
def OutcomeCode(txt):
  return OUTCOME_CODES[txt.lower()] if OUTCOME_CODES.has_key(txt.lower()) else OUTCOME_CODES['unspecified']

#############################################################################
def GetAssayResults_Screening2(base_url,aids,sids,fout,skip,nmax,verbose=0):
  '''One CSV line for each activity.  skip and nmax applied to AIDs.
In this version of the function, use the "concise" mode to download full data
for each AID, then iterate through SIDs and use local hash.
'''
  if verbose:
    if skip: print >>sys.stderr, 'skip: [1-%d]'%skip
    if nmax: print >>sys.stderr, 'NMAX: %d'%nmax
  n_aid_in=0; n_aid_done=0; n_out=0;
  nchunk_sid=100;
  #fout.write('aid,sid,outcome,version,rank,year\n')
  tags = None
  for aid in aids:
    n_aid_in+=1
    n_out_this=0;
    if skip and n_aid_in<skip: continue
    if nmax and n_aid_done>=nmax: break
    n_aid_done+=1
    if verbose>1:
      print >>sys.stderr, 'Request: (%d) [AID=%d] SID count: %d'%(n_aid_done,aid,len(sids))
    try:
      url = base_url+'/assay/aid/%d/concise/JSON'%(aid)
      print >>sys.stderr, 'DEBUG: %s'%(url)
      rval = rest_utils.GetURL(url,parse_json=True,verbose=verbose)
    except Exception, e:
      print >>sys.stderr, 'Error: %s'%(e)
      break

    if not type(rval)==types.DictType:
      #print >>sys.stderr, 'Error: %s'%(str(rval))
      f = open("z.z", "w")
      f.write(str(rval))
      f.close()
      print >>sys.stderr, 'DEBUG: rval not DictType.  See z.z'
      break
    adata = {} # data this assay
    tags_this = rval["Table"]["Columns"]["Column"]
    print >>sys.stderr, 'DEBUG: tags_this = %s'%(str(tags_this))
    j_sid = None;
    j_res = None;
    if not tags:
      tags = tags_this
      for j,tag in enumerate(tags):
        if tag == 'SID': j_sid = j
        if tag == 'Bioactivity Outcome': j_res = j
      fout.write(','.join(tags)+'\n')

    rows = rval["Table"]["Row"]

    for row in rows:
      cells = row["Cell"]
      if len(cells) != len(tags):
        print >>sys.stderr, 'Error: n_cells != n_tags (%d != %d)'%(len(cells), len(tags))
        continue

      sid = cells[j_sid]
      res = cells[j_res]
      adata[sid] = res

      #break #DEBUG

#############################################################################
def GetAssayResults_Screening(base_url,aids,sids,fout,skip,nmax,verbose=0):
  '''One CSV line for each activity.  skip and nmax applied to AIDs.
Must chunk the SIDs, since requests limited to 10k SIDs.
'''
  if verbose:
    if skip: print >>sys.stderr, 'skip: [1-%d]'%skip
    if nmax: print >>sys.stderr, 'NMAX: %d'%nmax
  n_aid_in=0; n_aid_done=0; n_out=0;
  nchunk_sid=100;
  fout.write('aid,sid,outcome,version,rank,year\n')
  for aid in aids:
    n_aid_in+=1
    n_out_this=0;
    if skip and n_aid_in<skip: continue
    if nmax and n_aid_done>=nmax: break
    n_aid_done+=1
    if verbose>1:
      print >>sys.stderr, 'Request: (%d) [AID=%d] SID count: %d'%(n_aid_done,aid,len(sids))
    nskip_sid=0;
    while True:
      if nskip_sid>=len(sids): break
      if verbose>1:
        print >>sys.stderr, '(%d) [AID=%s] ; SIDs [%d-%d of %d] ; measures: %d'%(n_aid_done,aid,nskip_sid+1,min(nskip_sid+nchunk_sid,len(sids)),len(sids),n_out_this)
      sidstr=(','.join(map(lambda x:str(x),sids[nskip_sid:nskip_sid+nchunk_sid])))
      try:
        rval = rest_utils.GetURL(base_url+'/assay/aid/%d/JSON?sid=%s'%(aid,sidstr),parse_json=True,verbose=verbose)
      except Exception, e:
        print >>sys.stderr, 'Error: %s'%(e)
        break
      if not type(rval)==types.DictType:
        print >>sys.stderr, 'Error: %s'%(str(rval))
        break
      pcac = rval['PC_AssayContainer'] if rval.has_key('PC_AssayContainer') else None
      if len(pcac)<1:
        print >>sys.stderr, 'Error: [%s] empty PC_AssayContainer.'%aid
        break
      if len(pcac)>1:
        print >>sys.stderr, 'NOTE: [%s] multiple assays in PC_AssayContainer.'%aid
      for assay in pcac:
        if not assay: continue
        if verbose>2:
          print >>sys.stderr, json.dumps(assay,indent=2)
        ameta = assay['assay'] if assay.has_key('assay') else None
        adata = assay['data'] if assay.has_key('data') else None
        if not ameta: print >>sys.stderr, 'Error: [%s] no metadata.'%aid
        if not adata: print >>sys.stderr, 'Error: [%s] no data.'%aid
        for datum in adata:
          sid = datum['sid'] if datum.has_key('sid') else ''
          outcome = datum['outcome'] if datum.has_key('outcome') else ''
          version = datum['version'] if datum.has_key('version') else ''
          rank = datum['rank'] if datum.has_key('rank') else ''
          date = datum['date'] if datum.has_key('date') else {}
          year = date['std']['year'] if date.has_key('std') and date['std'].has_key('year') else ''
          fout.write('%d,%s,%d,%s,%s,%s\n'%(aid,sid,OutcomeCode(outcome),version,rank,year))
          fout.flush()
          n_out_this+=1
      nskip_sid+=nchunk_sid
    if verbose>1:
      print >>sys.stderr, 'Result: [AID=%d] total measures: %d'%(aid,n_out_this)

  return n_aid_in,n_out

#############################################################################
def AssayXML2NameAndSource(xmlstr):
  '''Required: xpath - XPath Queries For DOM Trees, http://py-dom-xpath.googlecode.com/'''
  import xpath
  dom=xml.dom.minidom.parseString(xmlstr)
  tag_name='PC-AssayDescription_name'
  name=xpath.findvalue('//%s'%tag_name,dom)  ##1st
  tag_source='PC-DBTracking_name'
  source=xpath.findvalue('//%s'%tag_source,dom)  ##1st
  return name,source

#############################################################################
def DescribeAssay(base_url,id_query,verbose=0):
  rval=rest_utils.GetURL(base_url+'/assay/aid/%d/description/JSON'%id_query,parse_json=True,verbose=verbose)
  #print >>sys.stderr, json.dumps(rval,indent=2)
  assays = rval['PC_AssayContainer']
  print 'aid,name,assay_group,project_category,activity_outcome_method'
  for assay in assays:
    aid = assay['assay']['descr']['aid']['id']
    name = assay['assay']['descr']['name']
    assay_group = assay['assay']['descr']['assay_group'][0]
    project_category = assay['assay']['descr']['project_category']
    activity_outcome_method = assay['assay']['descr']['activity_outcome_method']
    vals = [aid,name,assay_group,project_category,activity_outcome_method]
    print (','.join(map(lambda s: '"%s"'%s, vals)))
  return

#############################################################################
def Name2Sids(base_url,name,verbose):
  d=rest_utils.GetURL(base_url+'/substance/name/%s/sids/JSON'%urllib.quote(name),parse_json=True,verbose=verbose)
  #return d[u'IdentifierList'][u'SID']
  return d['IdentifierList']['SID']

#############################################################################
def Sid2Synonyms(base_url,sid,verbose):
  d=rest_utils.GetURL(base_url+'/substance/sid/%d/synonyms/JSON'%(sid),parse_json=True,verbose=verbose)
  if not d: return []
  #if not type(d) is types.DictType: return []
  try:
    infos = d['InformationList']['Information']
  except Exception, e:
    print >>sys.stderr, 'Error (Exception): %s'%e
    print >>sys.stderr, 'DEBUG: d = %s'%str(d)
    return []
  if not infos: return []
  synonyms=[]
  for info in infos:
    synonyms.extend(info['Synonym'])
  return synonyms

#############################################################################
def Cid2Synonyms(base_url,cid,verbose):
  sids = Cid2Sids(base_url,cid,verbose)
  if verbose:
    print >>sys.stderr,'cid=%d: sid count: %d'%(cid,len(sids))
  synonyms = set([])
  for sid in sids:
    synonyms_this = Sid2Synonyms(base_url,sid,verbose)
    synonyms |= set(synonyms_this)
  return list(synonyms)

#############################################################################
def Cids2Synonyms(base_url,cids,fout,skip,nmax,verbose):
  fout.write('"cid","sids","synonyms"\n')
  sids = set([])
  i_cid=0;
  for cid in cids:
    i_cid+=1
    if skip and i_cid<=skip: continue
    sids_this = Cid2Sids(base_url,cid,verbose)
    sids |= set(sids_this)
    synonyms = set([])
    for sid in sids_this:
      synonyms_this = Sid2Synonyms(base_url,sid,verbose)
      synonyms |= set(synonyms_this)
    synonyms_nice = SortCompoundNamesByNiceness(list(synonyms))[:10]
    fout.write('%d,"%s","%s"\n'%(
	cid,
	';'.join(map(lambda x:str(x),sids_this)),
	';'.join(synonyms_nice)))
    if verbose:
      if synonyms_nice: s1=synonyms_nice[0]
      else: s1=None
      print >>sys.stderr,'%d. cid=%d: sids: %d ; synonyms: %d (%s)'%(i_cid,cid,len(sids_this),len(synonyms),s1)
    fout.flush()
    if nmax and i_cid>=(skip+nmax): break
  if verbose:
    print >>sys.stderr,'total sids: %d'%(len(sids))

#############################################################################
def Name2Cids(base_url,name,verbose):
  sids=Name2Sids(base_url,name,verbose)
  cids={}
  for cid in Sids2Cids(base_url,sids,verbose):
    cids[cid]=True
  cids=cids.keys()
  cids.sort() 
  return cids

#############################################################################
def NameNicenessScore(name):
  score=0;
  pat_proper = re.compile(r'^[A-Z][a-z]+$')
  pat_text = re.compile(r'^[A-Za-z ]+$')
  if pat_proper.match(name): score+=100
  elif pat_text.match(name): score+=50
  elif re.match(r'^[A-z][A-z][A-z][A-z][A-z][A-z][A-z].*$',name): score+=10
  if re.search(r'[\[\]\{\}]',name): score-=50
  if re.search(r'[_/\(\)]',name): score-=10
  if re.search(r'\d',name): score-=10
  score -= math.fabs(7-len(name))    #7 is optimal!
  return score

#############################################################################
### Heuristic for human comprehensibility.
#############################################################################
def SortCompoundNamesByNiceness(names):
  names_scored = {n:NameNicenessScore(n) for n in names}
  names_ranked = [[score,name] for name,score in names_scored.items()]
  names_ranked.sort()
  names_ranked.reverse()
  return [name for score,name in names_ranked]

#############################################################################
def GetCpdAssayStats(base_url,cid,smiles,aidset,fout_mol,fout_act,aidhash,verbose):
  aids_tested=set(); aids_active=set();
  sids_tested=set(); sids_active=set();
  n_sam=0; n_sam_active=0; mol_active=False; mol_found=False;

  try:
    fcsv=rest_utils.GetURL(base_url+'/compound/cid/%d/assaysummary/CSV'%cid,verbose=verbose)
  except urllib2.HTTPError,e:
    print >>sys.stderr, 'ERROR: [%d] REST request failed; response code = %d'%(cid,e.code)
    #if not http_errs.has_key(e.code): http_errs[e.code]=1
    #else: http_errs[e.code]+=1
    fout_mol.write("%s %d\n"%(smiles,cid))
    return mol_found,mol_active,n_sam,n_sam_active
  except Exception,e:
    print >>sys.stderr, 'ERROR: [%d] REST request failed; %s'%(cid,e)
    fout_mol.write("%s %d\n"%(smiles,cid))
    return mol_found,mol_active,n_sam,n_sam_active
  mol_found=True

  try:
    csvReader=csv.DictReader(fcsv.splitlines(),fieldnames=None,restkey=None,restval=None,dialect='excel',delimiter=',',quotechar='"')
    csvrow=csvReader.next()    ## must do this to get fieldnames
  except Exception,e:
    print >>sys.stderr, 'ERROR: [CID=%d] CSV problem:%s'%(cid,e)
    fout_mol.write("%s %d\n"%(smiles,cid))
    return mol_found,mol_active,n_sam,n_sam_active

  for field in ('AID','CID','SID','Bioactivity Outcome','Bioassay Type'):
    if field not in csvReader.fieldnames:
      print >>sys.stderr, 'ERROR: [CID=%d] bad CSV header, no "%s" field.'%(cid,field)
      print >>sys.stderr, 'DEBUG: fieldnames: %s'%(','.join(map((lambda x:'"%s"'%x),csvReader.fieldnames)))
      fout_mol.write("%s %d\n"%(smiles,cid))
      return mol_found,mol_active,n_sam,n_sam_active

  n_in=0
  while True:
    try:
      csvrow=csvReader.next()
    except:
      break  ## EOF
    n_in+=1

    try:
      aid=int(csvrow['AID'])
      sid=int(csvrow['SID'])
      csvrow_cid=int(csvrow['CID'])
    except:
      print >>sys.stderr, 'ERROR: [CID=%d] bad CSV line; problem parsing: "%s"'%(cid,str(csvrow))
      continue
    if cid!=csvrow_cid:
      print >>sys.stderr, 'ERROR: Aaack! [CID=%d] CID mismatch: != %d'%(cid,csvrow_cid)
      return mol_found,mol_active,n_sam,n_sam_active

    if aidset:
      if not aidset.has_key(aid):
        continue
      #print >>sys.stderr, 'DEBUG: AID [%d] ok (pre-selected).'%(aid)

    ## Assay filtering done; now update statistics (sTested, sActive).
    n_sam+=1
    aidhash[aid]=True
    act_outcome=csvrow['Bioactivity Outcome'].lower()
    if OUTCOME_CODES.has_key(act_outcome):
      fout_act.write("%d,%d,%d,%d\n"%(cid,sid,aid,OUTCOME_CODES[act_outcome]))
    else:
      if verbose>2:
        print >>sys.stderr, '[%d] unrecognized outcome (CID=%d,AID=%d): "%s"'%(n_in,cid,aid,act_outcome)

    aids_tested.add(aid)
    sids_tested.add(sid)
    if act_outcome=='active':
      n_sam_active+=1
      mol_active=True
      aids_active.add(aid)
      sids_active.add(sid)

  if verbose>2:
    print >>sys.stderr, '[CID=%d] CSV data lines: %d'%(cid,n_in)

  fout_mol.write("%s %d %d %d %d %d %d %d\n"%(
	smiles,
	cid,
	len(sids_tested),
	len(sids_active),
	len(aids_tested),
	len(aids_active),
	n_sam,
	n_sam_active))
  if verbose>1:
    print >>sys.stderr, (
	"cid=%d,sTested=%d,sActive=%d,aTested=%d,aActive=%d,wTested=%d,wActive=%d"%(
	cid,
	len(sids_tested),
	len(sids_active),
	len(aids_tested),
	len(aids_active),
	n_sam,
	n_sam_active))

  return mol_found,mol_active,n_sam,n_sam_active

#############################################################################
def GetCpdAssayData(base_url,cid_query,aidset,fout,verbose):

  try:
    fcsv=rest_utils.GetURL(base_url+'/compound/cid/%d/assaysummary/CSV'%cid_query,verbose=verbose)
  except Exception,e:
    print >>sys.stderr, 'ERROR: [%d] REST request failed; %s'%(cid_query,e)
    return False

  if not fcsv:
    return False

  try:
    csvReader=csv.DictReader(fcsv.splitlines(),fieldnames=None,restkey=None,restval=None,dialect='excel',delimiter=',',quotechar='"')
    csvrow=csvReader.next()    ## must do this to get fieldnames
  except Exception,e:
    print >>sys.stderr, 'ERROR: [CID=%d] CSV problem: %s'%(cid_query,e)
    return True

  for field in ('CID','SID','AID','Bioactivity Outcome','Activity Value [uM]'):
    if field not in csvReader.fieldnames:
      print >>sys.stderr, 'ERROR: [CID=%d] bad CSV header, no "%s" field.'%(cid_query,field)
      print >>sys.stderr, 'DEBUG: fieldnames: %s'%(','.join(map((lambda x:'"%s"'%x),csvReader.fieldnames)))
      return True

  n_in=0; n_act=0;
  while True:
    try:
      csvrow=csvReader.next()
    except:
      break  ## EOF
    n_in+=1
    try:
      aid=int(csvrow['AID'])
      sid=int(csvrow['SID'])
      cid=int(csvrow['CID'])
      outcome=csvrow['Bioactivity Outcome']
    except:
      print >>sys.stderr, 'ERROR: [CID=%d] bad CSV line; problem parsing.'%cid
      #print >>sys.stderr, 'DEBUG: csvrow = %s'%str(csvrow)
      continue
    if cid_query!=cid:
      print >>sys.stderr, 'ERROR: Aaack! [CID=%d] CID mismatch: != %d'%(cid,int(csvrow['CID']))
      return True
    if aid not in aidset:
      continue
      #print >>sys.stderr, 'DEBUG: AID [%d] ok (pre-selected).'%(aid)

    if not csvrow['Activity Value [uM]']:
      continue

    try:
      actval=float(csvrow['Activity Value [uM]'])
    except:
      print >>sys.stderr, 'ERROR: [CID=%d] bad CSV line; problem parsing activity: "%s"'%(cid,csvrow['Activity Value [uM]'])
      continue

    n_act+=1
    outcome_code = OUTCOME_CODES[outcome.lower()] if OUTCOME_CODES.has_key(outcome.lower()) else 0

    fout.write('%d,%d,%d,%d,%.3f\n'%(cid,sid,aid,outcome_code,actval))

  print >>sys.stderr, '[CID=%d] records: %2d ; activities: %2d'%(cid_query,n_in,n_act)
  return True

#############################################################################
if __name__=='__main__':

  if len(sys.argv)<2:
    print 'Syntax: %s NAMEFILE'%sys.argv[0]
    sys.exit(1)

  fin = open(sys.argv[1])
  while True:
    line = fin.readline()
    if not line: break
    name=line.rstrip()
    print '%s\t%d'%(name,NameNicenessScore(name))
