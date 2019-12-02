#!/usr/bin/env python3
###
# https://developer.twitter.com/en/docs/tweets/search/api-reference/get-search-tweets
# 7-day limit: no tweets found older than one week.
# Requests / 15-min window (user auth): 180
# Requests / 15-min window (app auth): 450
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
def SearchTwitter(hashtag, lang, result_type, api, n, fout):
  feed="search/tweets"
  count_perpage=100;
  n_out=0; n_req=0; i=0;
  while n_out < n:
    t0 = time.time()
    count = min(count_perpage, n - n_out)
    tweets  = [t for t in api.request(feed, {'q':('#'+hashtag), 'lang':lang, 'result_type':result_type, 'count':count})]
    n_req += 1
    df = pd.read_json(json.dumps(tweets))
    #print('{0!s}'.format(json.dumps(tweets, indent=4)), file=sys.stderr) #DEBUG
    #logging.debug('Response columns: {0!r}'.format(df.columns))
    #logging.debug('User fields: {0!r}'.format(df.user[1].keys()))
    #logging.debug("Mean tweet length: {0:.2f}".format(numpy.mean(df.text.str.len())))
    df_out = pd.DataFrame({'i':list(range(i+1, i+df.shape[0]+1)), 'id':df.id, 'created_at':df.created_at, 'lang':df.lang,
	'screen_name':[x['screen_name'] for x in df.user],
	'text':df.text.str.replace('[\n\r\t]', ' ')})
    df_out.to_csv(fout, '\t', header=bool(n_out==0), index=False)
    n_out += df.shape[0]
    i += df.shape[0]
    if n_req%10==0:
      logging.info('Progress: {0:6d}/{1:6d} tweets'.format(n_out, n))
    while time.time()-t0 < 6: #speed limit 10 requests/min
      time.sleep(1)

  logging.info("Output tweets: {0:d}".format(n_out))
  return

#############################################################################
if __name__=="__main__":
  PROG=os.path.basename(sys.argv[0])
  t0 = time.time()
  logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

  result_types = ['mixed', 'recent', 'popular']
  parser = argparse.ArgumentParser(description="Twitter API client: query for tweets (from previous 7 days)")
  parser.add_argument("--hashtag", required=True, help="hashtag")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--lang", default="en", help="language")
  parser.add_argument("--result_type", choices=result_types, default="mixed")
  parser.add_argument("--n", type=int, default=10, help="number of tweets to return")
  parser.add_argument("-v", "--verbose", action="count")
  args = parser.parse_args()

  if args.ofile:
    fout = open(args.ofile, "w")
  else:
    fout = sys.stdout

  ###
  toa = TwitterOAuth.read_file(os.environ['HOME']+'/.twitterapi_credentials')
  tapi = TwitterAPI(toa.consumer_key, toa.consumer_secret, toa.access_token_key, toa.access_token_secret)

  SearchTwitter(args.hashtag, args.lang, args.result_type, tapi, args.n, fout)

  logging.info(('%s: elapsed time: %s'%(PROG, time.strftime('%Hh:%Mm:%Ss', time.gmtime(time.time()-t0)))))
