#!/usr/bin/env python3
###
import sys,os,json,logging,argparse,time
import pandas as pd
import numpy
from TwitterAPI import TwitterAPI,TwitterOAuth

### Twitter API Credentials
# Credentials file format:
# consumer_key=YOUR_CONSUMER_KEY
# consumer_secret=YOUR_CONSUMER_SECRET
# access_token_key=YOUR_ACCESS_TOKEN
# access_token_secret=YOUR_ACCESS_TOKEN_SECRET
###

###
def SearchTwitter(q, lang, api, feed="search/tweets", n=100):
  return [t for t in api.request(feed, {'q':q, 'lang':lang, 'count':n})]

#############################################################################
if __name__=="__main__":
  PROG=os.path.basename(sys.argv[0])
  t0 = time.time()
  logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

  parser = argparse.ArgumentParser(description="Twitter API client: query and return TSV tweets")
  parser.add_argument("--query", required=True, help="query")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--lang", default="en", help="language")
  parser.add_argument("--n", type=int, default=100, help="number of tweets to return")
  parser.add_argument("-v", "--verbose", action="count")
  args = parser.parse_args()

  if args.ofile:
    fout = open(args.ofile, "w")
  else:
    fout = sys.stdout

  ###
  oauth = TwitterOAuth.read_file(os.environ['HOME']+'/.twitterapi_credentials')
  twapi = TwitterAPI(oauth.consumer_key, oauth.consumer_secret, oauth.access_token_key, oauth.access_token_secret)

  tweets = SearchTwitter('#'+args.query, args.lang, twapi, n=args.n)

  df = pd.read_json(json.dumps(tweets))

  logging.debug('Response columns: {0!r}'.format(df.columns))
  logging.debug('User fields: {0!r}'.format(df.user[1].keys()))
  logging.debug("Mean tweet length: {0:.2f}".format(numpy.mean(df.text.str.len())))

  df_out = pd.DataFrame({'id':df.id,
	'created_at':df.created_at,
	'lang':df.lang,
	'screen_name':[x['screen_name'] for x in df.user],
	'text':df.text.str.replace('[\n\r\t]', ' ')})

  df_out.to_csv(fout, '\t', index=False)

  logging.info(('%s: elapsed time: %s'%(PROG, time.strftime('%Hh:%Mm:%Ss', time.gmtime(time.time()-t0)))))
