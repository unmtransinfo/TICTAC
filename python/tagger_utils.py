#!/usr/bin/env python2
###
import sys,os,argparse

try:
  import tagger
except:
  sys.path.append("/home/app/tagger")
  import tagger

#############################################################################
if __name__=='__main__':
  parser = argparse.ArgumentParser(
	description='JensenLab Tagger NER utilities.')
  ops = ['tbe','tbe2']
  parser.add_argument("op",choices=ops,help='operation')
  parser.add_argument("--i",dest="ifile",help="input (CSV|TSV|SSV|TXT)")
  parser.add_argument("--o",dest="ofile",help="output (CSV|TSV)")
  parser.add_argument("-v","--verbose",action="count")
  args = parser.parse_args()

  if not args.ifile:
    parser.error('Input file required.')
  fin = open(args.ifile)

  if args.ofile:
    fout = open(args.ofile, "w")
  else:
    fout = sys.stdout

  tg = tagger.Tagger(java_script=None, re_stop=None, serials_only=False)

  doc = tg.load_local(args.ifile)


  #tg.get_entities(doc, docid, etypes)

  #tg.get_matches(doc, docid, etypes)
