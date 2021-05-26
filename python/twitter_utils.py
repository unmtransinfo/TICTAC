#!/usr/bin/env python3
###
# https://developer.twitter.com/en/docs/tweets/search/api-reference/get-search-tweets
###
# NEW: Twitter API v2
# https://developer.twitter.com/en/docs/twitter-api/tweets/search/introduction
# https://github.com/geduldig/TwitterAPI
###
# 7-day limit: no tweets found older than one week.
# Requests / 15-min window (user auth): 180
# Requests / 15-min window (app auth): 450
###
import sys,os,json,logging,argparse,time,tqdm
import pandas as pd
import numpy
import fsspec
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
  count_perpage=100; n_out=0; n_req=0; i=0; tq=None;
  while n_out < n:
    t0 = time.time()
    if tq is None: tq = tqdm.tqdm(total=n, unit="tweets")
    count = min(count_perpage, n - n_out)
    #tweets  = [t for t in api.request("search/tweets", {'q':('#'+hashtag), 'lang':lang, 'result_type':result_type, 'count':count})]
    try:
      response  = api.request("tweets/search/recent", {'query':hashtag, 'lang':lang, 'result_type':result_type, 'count':count})
    except Exception as e:
      logging.debug(f"status_code={response.status_code}")
      logging.error(e)
      break
    tweets  = [tweet for tweet in response]
    logging.debug(tweets)
    n_req += 1
    logging.debug(json.dumps(tweets, indent=4))
    df = pd.read_json(json.dumps(tweets))
    logging.debug(f"Response columns: {df.columns!r}")
    logging.debug(f"User fields: {df.user[1].keys()!r}")
    logging.debug(f"Mean tweet length: {numpy.mean(df.text.str.len()):.2f}")
    df_out = pd.DataFrame({'i':list(range(i+1, i+df.shape[0]+1)), 'id':df.id, 'created_at':df.created_at, 'lang':df.lang,
	'screen_name':[x['screen_name'] for x in df.user],
	'text':df.text.str.replace('[\n\r\t]', ' ')})
    df_out.to_csv(fout, '\t', header=bool(n_out==0), index=False)
    n_out += df.shape[0]
    tq.update(n_out)
    i += df.shape[0]
    while time.time()-t0 < 6: #speed limit 10 requests/min
      time.sleep(1)
  tq.close()
  logging.info(f"Output tweets: {n_out}")

#############################################################################
if __name__=="__main__":
  RESULT_TYPES = ['mixed', 'recent', 'popular']
  parser = argparse.ArgumentParser(description="Twitter API client: query for tweets (from previous 7 days)")
  parser.add_argument("--hashtag", required=True, help="hashtag")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--lang", default="en", help="language")
  parser.add_argument("--result_type", choices=RESULT_TYPES, default="mixed")
  parser.add_argument("--n", type=int, default=10, help="number of tweets to return")
  parser.add_argument("-v", "--verbose", default=0, action="count")
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  t0 = time.time()
  fout = open(args.ofile, "w") if args.ofile else sys.stdout

  ###
  toa = TwitterOAuth.read_file(os.environ['HOME']+'/.twitterapi_credentials')
  tapi = TwitterAPI(toa.consumer_key, toa.consumer_secret, toa.access_token_key, toa.access_token_secret, api_version="2")

  SearchTwitter(args.hashtag, args.lang, args.result_type, tapi, args.n, fout)

  logging.info(f"""Elapsed time: {time.strftime('%Hh:%Mm:%Ss', time.gmtime(time.time()-t0))}""")
