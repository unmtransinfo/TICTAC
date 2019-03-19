#!/usr/bin/env python
'''
Commonly used functions for REST client applications.

* JSON and XML handled, parsed into objects.
* HTTP headers and POST data handled.

HTTP "error" code 404 is not an error!
Return value None indicates an error.  
Return value [] indicates an not found, no data.  

Jeremy Yang
10 Aug 2017
'''
import sys,os,re,time,types
import urllib,urllib2,httplib,base64
import json
from xml.etree import ElementTree
from xml.parsers import expat
#
REST_TIMEOUT=10
REST_RETRY_NMAX=10
REST_RETRY_WAIT=5
#
##############################################################################
def GetURL(url,headers={},parse_json=False,usr=None,pw=None,parse_xml=False,nmax_retry=REST_RETRY_NMAX,verbose=0):
  '''Entry point for GET requests.'''
  return RequestURL(url,headers,None,usr,pw,parse_json,parse_xml,nmax_retry,verbose)

##############################################################################
def PostURL(url,headers={},data={},usr=None,pw=None,parse_json=False,parse_xml=False,nmax_retry=REST_RETRY_NMAX,verbose=0):
  '''Entry point for POST requests.'''
  return RequestURL(url,headers,data,usr,pw,parse_json,parse_xml,nmax_retry,verbose)

##############################################################################
def RequestURL(url,headers,data,usr,pw,parse_json,parse_xml,nmax_retry,verbose):
  '''Use internally, not externally.  Called by GetURL() and PostURL().  Only Basic authentication supported.'''
  if type(data) == types.DictType:
    data=urllib.urlencode(data)
  req=urllib2.Request(url=url,headers=headers,data=data)
  if usr and pw:
    req.add_header("Authorization", "Basic %s"%base64.encodestring('%s:%s'%(usr,pw)).replace('\n','')) 

  if verbose>1:
    print >>sys.stderr, 'url="%s"'%url
  if verbose>2:
    print >>sys.stderr, 'request type = %s'%req.get_type()
    print >>sys.stderr, 'request method = %s'%req.get_method()
    print >>sys.stderr, 'request host = %s'%req.get_host()
    print >>sys.stderr, 'request full_url = %s'%req.get_full_url()
    print >>sys.stderr, 'request header_items = %s'%req.header_items()
    if data:
      print >>sys.stderr, 'request data = %s'%req.get_data()
      print >>sys.stderr, 'request data size = %s'%len(req.get_data())

  i_try=0
  while True:
    i_try+=1
    try:
      f=urllib2.urlopen(req,timeout=REST_TIMEOUT)
      #f=urllib2.urlopen(req)
      if not f:
        print >>sys.stderr, 'ERROR: urlopen failed.'
        return None
      ftxt=f.read()
      f.close()
    except urllib2.HTTPError, e:
      if e.code==404:
        return ([])
      print >>sys.stderr, 'HTTP Error: %s'%e
      return None
    except urllib2.URLError, e:  ## may be socket.error
      # may be "<urlopen error [Errno 110] Connection timed out>"
      print >>sys.stderr, 'URLError [try %d/%d]: %s'%(i_try,nmax_retry,e)
      if i_try<nmax_retry:
        time.sleep(REST_RETRY_WAIT)
        continue
      return None
    except httplib.BadStatusLine, e:
      print >>sys.stderr, 'Error (BadStatusLine):  [try %d/%d]: %s'%(i_try,nmax_retry,e)
      if i_try<nmax_retry:
        time.sleep(REST_RETRY_WAIT)
        continue
      return None
    except Exception, e:
      print >>sys.stderr, 'Error (Exception): %s'%e
      if i_try<nmax_retry:
        time.sleep(REST_RETRY_WAIT)
        continue
      return None
    break

  if ftxt.strip()=='': return None

  if parse_json:
    try:
      rval=json.loads(ftxt.decode('unicode_escape'), encoding='utf_8')
    except ValueError, e:
      try:
        ### Should not be necessary.  Backslash escapes allowed in JSON.
        ftxt_fix=ftxt.replace(r'\"','&quot;').replace(r'\\','')
        ftxt_fix=ftxt_fix.replace(r'\n','\\\\n') #ok?
        rval=json.loads(ftxt_fix.decode('unicode_escape'), encoding='utf_8')
        if verbose>1:
          print >>sys.stderr, 'Apparently fixed JSON Error: %s'%e
        if verbose>2:
          print >>sys.stderr, 'DEBUG: Apparently fixed JSON: "%s"'%ftxt
          #sys.exit()
      except ValueError, e:
        if verbose:
          print >>sys.stderr, 'Failed to fix JSON Error: %s'%e
          print >>sys.stderr, 'DEBUG: ftxt_fix="%s"'%ftxt_fix
        rval=ftxt
  elif parse_xml:
    try:
      rval=ParseXml(ftxt)
    except Exception, e:
      if verbose: print >>sys.stderr, 'XML Error: %s'%e
      rval=ftxt
  else: #raw
    rval=ftxt

  return rval

#############################################################################
def ParseXml(xml_str):
  doc=None
  try:
    doc=ElementTree.fromstring(xml_str)
  except Exception, e:
    print >>sys.stderr,'XML parse error: %s'%e
    return False
  return doc

#############################################################################
