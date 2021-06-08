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
import sys,os,re,json,logging,argparse,time,tqdm
import pandas as pd
import numpy
import fsspec
from TwitterAPI import TwitterAPI,TwitterOAuth,TwitterPager,TwitterRequestError,TwitterConnectionError

### Twitter API Credentials
# Credentials file format:
# consumer_key=YOUR_CONSUMER_KEY
# consumer_secret=YOUR_CONSUMER_SECRET
# access_token_key=YOUR_ACCESS_TOKEN
# access_token_secret=YOUR_ACCESS_TOKEN_SECRET
###

###
def SearchTwitter(query, lang, result_type, api, n, fout):
  n_out=0; tq=None; df=None;
  try:
    pager = TwitterPager(api, 'tweets/search/recent', {'query':query})
    for tweet in pager.get_iterator(new_tweets=False):
      t0 = time.time()
      if tq is None: tq = tqdm.tqdm(total=n, unit="tweets")
      logging.debug(tweet)
      text = re.sub(r'[\n\r\t ]+', ' ', tweet["text"])
      df_this = pd.DataFrame({"id":[tweet["id"]], "text":[text]})
      if fout is None: df = pd.concat([df, df_this])
      else: df_this.to_csv(fout, '\t', header=bool(n_out==0), index=False)
      n_out += df_this.shape[0]
      tq.update(df_this.shape[0])
      if n_out>=n: break
  except TwitterRequestError as e:
    print(e.status_code)
    for msg in iter(e):
      print(msg)

  except TwitterConnectionError as e:
    print(e)

  except Exception as e:
    print(e)

  tq.close()
  logging.info(f"Output tweets: {n_out}")
  if fout is None:
    return df

#############################################################################
if __name__=="__main__":
  RESULT_TYPES = ['mixed', 'recent', 'popular']
  parser = argparse.ArgumentParser(description="Twitter API client: query for tweets (from previous 7 days)")
  parser.add_argument("--query", required=True, help="query")
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
  logging.debug(f"consumer_key={toa.consumer_key}; consumer_secret={toa.consumer_secret}; access_token_key={toa.access_token_key}; access_token_secret={toa.access_token_secret}")
  tapi = TwitterAPI(toa.consumer_key, toa.consumer_secret, toa.access_token_key, toa.access_token_secret, api_version="2")

  SearchTwitter(args.query, args.lang, args.result_type, tapi, args.n, fout)

  logging.info(f"""Elapsed time: {time.strftime('%Hh:%Mm:%Ss', time.gmtime(time.time()-t0))}""")
