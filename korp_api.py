import urllib
import pandas
import collections
import wget
import os
import json
import codecs
import numpy
from scipy.stats import binom
import time


URL_COM = "https://korp.csc.fi/korp/api8/COMMAND?defaultcontext=DEFAULT_CONTEXT&cache=true"
URL_GROUPBY = "group_by=GROUPBY"
URL_SHOW = "show=SHOW"
URL_STRUCT_KLK = "show_struct=text_label.text_publ_(title.id).text_issue_(date.no.title).text_(elec_date.language.page_no.sentcount.tokencount.img_url.publ_type).paragraph_id.sentence_(id.parse_state.local_id).text_binding_id.text_page_image_(url.context_url).text_download_pdf_url"
URL_START_END = "&start=START&end=END"
URL_CORPUS_KLK = "corpus=" + "%2C".join([f"KLK_FI_{i}" for i in range(1860,1900)])
URL_CORPUS_S24 = "corpus=" + "%2C".join([f"S24_{i}" for i in range(2001,2021)])
#GlobWE text_country, text_year, text_genre
URL_CORPUS_GLOBWE = "corpus=GLOWBE_(US_GENL.US_BLOG.CA_GENL.CA_BLOG.GB_GENL.GB_BLOG.IE_GENL.IE_BLOG.AU_GENL.AU_BLOG.NZ_GENL.NZ_BLOG.IN_GENL.IN_BLOG.LK_GENL.LK_BLOG.PK_GENL.PK_BLOG.BD_GENL.BD_BLOG.SG_GENL.SG_BLOG.MY_GENL.MY_BLOG.PH_GENL.PH_BLOG.HK_GENL.HK_BLOG.ZA_GENL.ZA_BLOG.NG_GENL.NG_BLOG.GH_GENL.GH_BLOG.KE_GENL.KE_BLOG.TZ_GENL.TZ_BLOG.JM_GENL.JM_BLOG)"
#COHA text_genre, text_year
URL_CORPUS_COHA = "corpus=COHA_1810S_FIC%2CCOHA_1810S_MAG%2CCOHA_1810S_NF%2CCOHA_1820S_FIC%2CCOHA_1820S_MAG%2CCOHA_1820S_NF%2CCOHA_1830S_FIC%2CCOHA_1830S_MAG%2CCOHA_1830S_NF%2CCOHA_1840S_FIC%2CCOHA_1840S_MAG%2CCOHA_1840S_NF%2CCOHA_1850S_FIC%2CCOHA_1850S_MAG%2CCOHA_1850S_NF%2CCOHA_1860S_FIC%2CCOHA_1860S_MAG%2CCOHA_1860S_NEWS%2CCOHA_1860S_NF%2CCOHA_1870S_FIC%2CCOHA_1870S_MAG%2CCOHA_1870S_NEWS%2CCOHA_1870S_NF%2CCOHA_1880S_FIC%2CCOHA_1880S_MAG%2CCOHA_1880S_NEWS%2CCOHA_1880S_NF%2CCOHA_1890S_FIC%2CCOHA_1890S_MAG%2CCOHA_1890S_NEWS%2CCOHA_1890S_NF%2CCOHA_1900S_FIC%2CCOHA_1900S_MAG%2CCOHA_1900S_NEWS%2CCOHA_1900S_NF%2CCOHA_1910S_FIC%2CCOHA_1910S_MAG%2CCOHA_1910S_NEWS%2CCOHA_1910S_NF%2CCOHA_1920S_FIC%2CCOHA_1920S_MAG%2CCOHA_1920S_NEWS%2CCOHA_1920S_NF%2CCOHA_1930S_FIC%2CCOHA_1930S_MAG%2CCOHA_1930S_NEWS%2CCOHA_1930S_NF%2CCOHA_1940S_FIC%2CCOHA_1940S_MAG%2CCOHA_1940S_NEWS%2CCOHA_1940S_NF%2CCOHA_1950S_FIC%2CCOHA_1950S_MAG%2CCOHA_1950S_NEWS%2CCOHA_1950S_NF%2CCOHA_1960S_FIC%2CCOHA_1960S_MAG%2CCOHA_1960S_NEWS%2CCOHA_1960S_NF%2CCOHA_1970S_FIC%2CCOHA_1970S_MAG%2CCOHA_1970S_NEWS%2CCOHA_1970S_NF%2CCOHA_1980S_FIC%2CCOHA_1980S_MAG%2CCOHA_1980S_NEWS%2CCOHA_1980S_NF%2CCOHA_1990S_FIC%2CCOHA_1990S_MAG%2CCOHA_1990S_NEWS%2CCOHA_1990S_NF%2CCOHA_2000S_FIC%2CCOHA_2000S_MAG%2CCOHA_2000S_NEWS%2CCOHA_2000S_NF"
#COCA text_genre, text_year, text_subgenre, text_source
URL_CORPUS_COCA = "corpus=COCA_(FIC.MAG.NEWS.ACAD.SPOK)"
URL_ENDBITS =  "context=&incremental=true&defaultwithin=sentence&within=&loginfo=lang%3Dfi+search%3Dadv"
URL_QUERY = "cqp=QUERY"

def list_collocations(lemma, corpus, rang, crop=[]):
  print(type(crop))
  if type(crop) == str: 
    crop=[crop]
  query = '[lemma="'+lemma+'"'+' & '.join([x.split(":")[0]+'='+'"'+x.split(":")[1]+'"' for x in crop])+']'
  print(query)
  count_occurrences = download(query_occurrences(query, corpus, "1"))['hits']
  collocations = []
  for i in range(0, count_occurrences, 100000):
    t0 = time.time()
    start = i
    end = min(count_occurrences, start+99999)
    url = query_occurrences(query, corpus, end, start=start, context=str(rang)+'+words', show="lemma")
    occurrences = download(url)['kwic']
    collocations.extend([y['lemma'] for x in occurrences for y in x['tokens']])
    print(time.time()-t0)
  

  collocations = collections.Counter(collocations)
  return pandas.Series(collocations)

def build_frequency_table(corpus):
  if corpus == "klk":
    return build_frequency_table_for_klk()
  elif corpus == "suomi24":
    return build_frequency_table_for_s24()

def build_frequency_table_for_s24():
  source_root_url = "https://raw.githubusercontent.com/kannera/keyword_course2021/main/s24_unigrams/"
  res = dict()
  for i in range(2001, 2020):
    print(source_root_url+str(i)+".json")
    data = download(source_root_url+str(i)+".json")
    res[i] = data
  print(query_frequencies("", "text_empty", "s24").replace("count", "corpus_info"))
  tf = download(query_frequencies("", "", "suomi24").replace("count", "corpus_info"))['total_size']
  return pandas.DataFrame(res).fillna(1).sum(axis=1), tf

def build_frequency_table_for_klk():
  source_root_url = "https://raw.githubusercontent.com/kannera/keyword_course2021/main/klk_unigrams/"
  res = dict()
  for i in range(1860, 1900):
    print(source_root_url+str(i)+".json")
    data = download(source_root_url+str(i)+".json")
    res[i] = data
  print(query_frequencies("", "text_publ_type", "klk").replace("count", "corpus_info"))
  tf = download(query_frequencies("", "text_publ_type", "klk").replace("count", "corpus_info"))['total_size']
  return pandas.DataFrame(res).fillna(1).sum(axis=1), tf

def build_collocation_table(frequencies, tf, lemma, corpus, rang, crop):
  collocations = list_collocations(lemma, corpus, 5)
  collocations_df = pandas.DataFrame(collocations)
  collocations_df['w2'] = frequencies
  collocations_df['w1'] = collocations_df.loc[lemma]['w2']
  collocations_df['w12'] = collocations_df[0]
  collocations_df['tf'] = tf
  collocations_df['pmi'] = collocations_df.apply(pmi, axis=1)
  collocations_df['t-test'] = collocations_df.apply(t_test, axis=1)
  collocations_df['llr'] = collocations_df.apply(llr, axis=1)
  return collocations_df



def pmi(X):
  w1 = X['w1']
  w2 = X['w2']
  w12 = X['w12']
  tf = X['tf']

  return numpy.log((w12/tf)/((w1/tf)*(w2/tf)))

def bd(k, n, p):
  return binom.logpmf(k, n, p)

def llr(X):

  w1 = X['w1']
  w2 = X['w2']
  w12 = X['w12']
  tf = X['tf']

  p = w2/tf
  p1 = w12/w1
  p2 = (w2-w12)/(tf-w1)

  bn1 = bd(w12, w1, p)
  bn2 = bd(w2-w12, tf-w1, p)
  bn3 = bd(w12, w1, p1)
  bn4 = bd(w2-w12, tf-w1, p2)
  return -2*(bn1+bn2-bn3-bn4)

def t_test(X):
  w1 = X['w1']
  w2 = X['w2']
  w12 = X['w12']
  tf = X['tf']

  p1 = w1/tf
  p2 = w2/tf
  p0 = p1 * p2

  ps  = w12/tf

  score = (ps - p0) / numpy.sqrt((ps/tf))

  return score

def query_full_corpus_sizes(corpus, query=""):
  if corpus == "klk":
    url = query_frequencies(query, "text_issue_date", "klk")
    if query == "":
      url = url.replace("count", "count_all")
    data = download(url)['total']['absolute']
    data = [{"text_issue_date":k, "frequency":v} for k,v in data.items()]
    data = pandas.DataFrame(data)
    if "text_issue_date" in data.columns:
      data = add_date_columns_for_klk(data)
    return data
  
  if corpus == "suomi24":
    url = query_frequencies("", 'text_topic_name_leaf', "suomi24")
    url = url.replace("count", "count_all")
    print(url)
    data = download(url)['total']['absolute']
    data = [{'text_topic_name_leaf':k, "frequency":v} for k,v in data.items()]
    data = pandas.DataFrame(data)
    #data = add_date_columns_for_klk(data)
    return data

def add_date_columns_for_klk(df):
  df['date'] = df['text_issue_date'].apply(lambda x:parse_date(x) if x.count(".") == 2 else "no date")
  df['text_issue_date'] = df['text_issue_date'].apply(lambda x: "01."+x if x.count(".") == 0 else x)
  df['text_issue_date'] = df['text_issue_date'].apply(lambda x: "01."+x if x.count(".") == 1 else x)
  df['month_date'] = df['text_issue_date'].apply(lambda x:x.split(".")[-1]+"-"+x.split(".")[1]+"-01")
  df['year'] = df['text_issue_date'].apply(lambda x:x.split(".")[-1])
  df['decade'] = df['year'].apply(lambda x:x[:-1]+"0")
  
  return df

def query_frequencies(query, groupby, corpus, allfr=False):
  url_bits = [URL_COM.replace("COMMAND", "count"), URL_GROUPBY.replace("GROUPBY", groupby), URL_QUERY.replace("QUERY", urllib.parse.quote_plus(query)), URL_ENDBITS]
  
    
  if corpus == "klk":
    url_bits.append(URL_CORPUS_KLK)
  elif corpus == "suomi24" or corpus == "s24":
    url_bits.append(URL_CORPUS_S24)
  elif corpus == "globwe":
    url_bits.append(URL_CORPUS_GLOBWE)
  elif corpus == "coca":
    url_bits.append(URL_CORPUS_COCA)
  elif corpus == "coha":
    url_bits.append(URL_CORPUS_COHA)
  url = "&".join(url_bits)
  if allfr:
    url = url.replace("count", "count_all")
  return url

def download(url):
  #with open("cookies.txt", "r", encoding="utf-8") as f:
  #  print([x for x in f])
  #os.system('wget --load-cookies=cookies.txt "'+url+'" -O tmp.json')
  tmp = wget.download(url, out="tmp.json")
  with codecs.open("tmp.json", "r", encoding="utf-8", errors="replace") as f:
    data = json.load(f)
  
  #os.remove("tmp.json")
  os.remove(tmp)
  return data

def parse_date(x):
  x = x.split(".")
  return x[-1]+"-"+x[1]+"-"+x[0]

#THIS IS USED IN THE ASSIGNMENT:frequencies NOTEBOOK
def get_frequency_data_from_korp(query, groupby, corpus, sums=False, mode=False):
  
  
  url = query_frequencies(query, groupby, corpus)
  print(url)
  if not mode:
    data = download(url)
  
  elif mode == "url":
    return url
  
  else:
    with open(input, "r", encoding="utf-8") as f:
      data = json.load(f)
      
  key = "total"
  if key not in data: key = "combined"
  
  if sums:
    return {"abs_frequency":data[key]['sums']['absolute'], "rel_frequency":data[key]['sums']['relative']}
  else:
    data = [{groupby:k, "rel_frequency":v, "abs_frequency":data[key]['absolute'][k]} for k,v in data[key]['relative'].items()]
    df = pandas.DataFrame(data)
  if corpus == "klk" and "text_issue_date" in df.columns:
    return add_date_columns_for_klk(df)
  else:
    return df

def read_occurrences(query, corpus,n):
  url = query_occurrences(query, corpus, n)
  data = download(url)
  print(data)
  return data["kwic"]

def query_occurrences(query, corpus, n, start=0, context="1+sentence", show=""):
  url_bits = [URL_COM.replace("COMMAND", "query").replace("DEFAULT_CONTEXT",context), URL_SHOW.replace("SHOW", show), URL_STRUCT_KLK, URL_START_END.replace("END", str(n)).replace("START", str(start)), URL_QUERY.replace("QUERY", urllib.parse.quote_plus(query)), URL_ENDBITS]
  if corpus == "klk":
    url_bits.append(URL_CORPUS_KLK)
  elif corpus == "suomi24":
    url_bits.append(URL_CORPUS_S24)
  elif corpus == "globwe":
    url_bits.append(URL_CORPUS_GLOBWE)
  elif corpus == "coca":
    url_bits.append(URL_CORPUS_COCA)
  elif corpus == "coha":
    url_bits.append(URL_CORPUS_COHA)
  url = "&".join(url_bits)
  return url
