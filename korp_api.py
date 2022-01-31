import urllib
import pandas
import wget
import os
import json

URL_COM = "https://korp.csc.fi/cgi-bin/korp/korp.cgi?command=COMMAND&defaultcontext=1+sentence&cache=true"
URL_GROUPBY = "groupby=GROUPBY"
URL_SHOW = "show=sentence.paragraph.lemma(.comp).pos.msd.dep(head.rel).ref"
URL_STRUCT_KLK = "show_struct=text_label.text_publ_(title.id).text_issue_(date.no.title).text_(elec_date.language.page_no.sentcount.tokencount.img_url.publ_type).paragraph_id.sentence_(id.parse_state.local_id).text_binding_id.text_page_image_(url.context_url).text_download_pdf_url"
URL_START_END = "&start=START&end=END"
URL_CORPUS_KLK = "corpus=KLK_FI_18%2899.98.97.96.95.94.93.92.91.90.89.88.87.86.85.84.83.82.81.80.79.78.77.76.75.74.73.72.71.70.69.68.67.66.65.64.63.62.61.60%29"
URL_CORPUS_S24 = "corpus=S24_200%281.2.3.4.5.6.7.8.9%29.S24_201%280.1.2.3.4.5.6.7.8.9%29.S24_2020"
#GlobWE text_country, text_year, text_genre
URL_CORPUS_GLOBWE = "corpus=GLOWBE_(US_GENL.US_BLOG.CA_GENL.CA_BLOG.GB_GENL.GB_BLOG.IE_GENL.IE_BLOG.AU_GENL.AU_BLOG.NZ_GENL.NZ_BLOG.IN_GENL.IN_BLOG.LK_GENL.LK_BLOG.PK_GENL.PK_BLOG.BD_GENL.BD_BLOG.SG_GENL.SG_BLOG.MY_GENL.MY_BLOG.PH_GENL.PH_BLOG.HK_GENL.HK_BLOG.ZA_GENL.ZA_BLOG.NG_GENL.NG_BLOG.GH_GENL.GH_BLOG.KE_GENL.KE_BLOG.TZ_GENL.TZ_BLOG.JM_GENL.JM_BLOG)"
#COHA text_genre, text_year
URL_CORPUS_COHA = "corpus=COHA_1810S_(FIC.MAG.NF).COHA_1820S_(FIC.MAG.NF).COHA_1830S_(FIC.MAG.NF).COHA_1840S_(FIC.MAG.NF).COHA_1850S_(FIC.MAG.NF).COHA_1860S_(FIC.MAG.NEWS.NF).COHA_1870S_(FIC.MAG.NEWS.NF).COHA_1880S_(FIC.MAG.NEWS.NF).COHA_1890S_(FIC.MAG.NEWS.NF).COHA_1900S_(FIC.MAG.NEWS.NF).COHA_1910S_(FIC.MAG.NEWS.NF).COHA_1920S_(FIC.MAG.NEWS.NF).COHA_1930S_(FIC.MAG.NEWS.NF).COHA_1940S_(FIC.MAG.NEWS.NF).COHA_1950S_(FIC.MAG.NEWS.NF).COHA_1960S_(FIC.MAG.NEWS.NF).COHA_1970S_(FIC.MAG.NEWS.NF).COHA_1980S_(FIC.MAG.NEWS.NF).COHA_1990S_(FIC.MAG.NEWS.NF).COHA_2000S_(FIC.MAG.NEWS.NF)"
#COCA text_genre, text_year, text_subgenre, text_source
URL_CORPUS_COCA = "corpus=COCA_(FIC.MAG.NEWS.ACAD.SPOK)"
URL_ENDBITS =  "context=&incremental=true&defaultwithin=sentence&within=&loginfo=lang%3Dfi+search%3Dadv"
URL_QUERY = "cqp=QUERY"

def query_frequencies(query, groupby, corpus):
  url_bits = [URL_COM.replace("COMMAND", "count"), URL_GROUPBY.replace("GROUPBY", groupby), URL_QUERY.replace("QUERY", urllib.parse.quote_plus(query)), URL_ENDBITS]
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

def download(url):
  wget.download(url, out="tmp.json")
  with open("tmp.json", "r", encoding="utf-8") as f:
    data = json.load(f)
  os.remove("tmp.json")
  return data

def parse_date(x):
  x = x.split(".")
  return x[-1]+"-"+x[1]+"-"+x[0]

def get_frequency_data_from_korp(query, groupby, corpus):
  url = query_frequencies(query, groupby, corpus)
  data = download(url)
  
  data = [{groupby:k, "rel_frequency":v, "abs_frequency":data['total']['absolute'][k]} for k,v in data['total']['relative'].items()]
  
  df = pandas.DataFrame(df)
  return
