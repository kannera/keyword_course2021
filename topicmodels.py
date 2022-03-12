import wget
import json, os, re, sys
import pandas, numpy
import urllib.parse

def download_topic_model(corpus, n_topics):
  MODEL_URL = "https://raw.githubusercontent.com/kannera/keyword_course2021/main/topic_models/CORPUS_N-TOPIC_TABLE.csv"
  
  url = MODEL_URL.replace("N-TOPIC", str(n_topics)).replace("CORPUS", corpus).replace("TABLE", "wbt")
  print(url)
  tmp = wget.download(url)
  wbt = pandas.read_csv(tmp, index_col=0)
  os.remove(tmp)

  url = MODEL_URL.replace("N-TOPIC", str(n_topics)).replace("CORPUS", corpus).replace("TABLE", "dbt")
  tmp = wget.download(url)
  dbt = pandas.read_csv(tmp, index_col=0)
  os.remove(tmp)

  return wbt, dbt

def print_series_side_by_side(A, B):
  
  for a,b in zip(A.index, B.index):
    line = [str(a), str(round(A.loc[a], 2)), str(b), str(round(B.loc[b], 2))]
    line = [x+blanks(20-len(x)) for x in line]
    print("".join(line))

def blanks(N):
  return "".join([" " for i in range(N)])

def view_topic_words(topic_model, top_n, which_topics="all"):
  wbt, dbt = topic_model
  if which_topics == "all":
    which_topics = wbt.columns
  elif type(which_topics) == int: which_topics = [which_topics]
  wbt = wbt.fillna(0)
  wbt_rel = wbt / wbt.sum(axis=1)[:, numpy.newaxis]
  for c in list(wbt.columns):
    if int(c) not in which_topics and str(c) not in which_topics: continue
    print("topic size:", wbt[c].sum())
    print_series_side_by_side(wbt[c].sort_values(ascending=False).head(top_n), wbt_rel[c].sort_values(ascending=False).head(top_n))
    print("*****")
 
def topics_over_word(topic_model, lemma):
  wbt,dbt = topic_model
  print(wbt.loc[lemma])
  
def read_text(corpus, text_id):
  if corpus == "suomi24":
    text = query_thread_from_korp(text_id)
  if corpus == "glowbe":
    text = query_texts_from_git(text_id)
  print(text)
  
def query_texts_from_git(text_id):
  METADATA_URL = "https://raw.githubusercontent.com/kannera/keyword_course2021/main/glowbe_metadata.tsv"
  TEXT_URL = "https://raw.githubusercontent.com/kannera/keyword_course2021/main/glowbe/COUNTRY_1.txt"
  tmp = wget.download(METADATA_URL)
  metadata = pandas.read_csv(tmp, index_col=0, sep="\t")
  os.remove(tmp)
  country = metadata.loc[int(text_id)]['country|genre'].split(" ")[0].lower()
  text_url = TEXT_URL.replace("COUNTRY", country)
  tmp = wget.download(text_url)
  with open(tmp, "r", encoding="utf-8") as f:
    textdata = [x[:-1].split("\t") for x in f]
  textdata = pandas.DataFrame(textdata, columns = ["text_id", "word", "lemma"])
  textdata = textdata[textdata['text_id'] == text_id]['word']
  lines = []
  
  for i,w in enumerate(list(textdata)):
    if i == 0: line = w
    if w == "<p>" or w == "<h>":
      line += "\n"
      lines.append(line)
      line = ""
    else:
      if len(line) == 0:
        line = w
      elif len(line) > 40:
          if w in (".", ",", ":", '"', ";"):
            line += w
            lines.append(line)
            line = ""
          else:
            lines.append(line)
            line = w
      else:
        if w not in (".", ",", ":", '"', ";"):
          line += " "
        line += w
  return "\n".join(lines)

def view_topic_docs(topic_model, top_n, which_topics="all"):
  wbt, dbt = topic_model
  if which_topics == "all":
    which_topics = dbt.columns
  elif type(which_topics) == int: which_topics = [which_topics]
  for c in list(dbt.columns):
    if int(c) not in which_topics and str(c) not in which_topics: continue
    print("topic size:", dbt[c].sum())
    print(dbt[c].sort_values(ascending=False).head(top_n))
    print("*****")
    
def query_thread_from_korp(text_id):
  URL = "https://korp.csc.fi/korp/api8/query?default_context=1%20sentence&show=sentence%2Cparagraph%2Clemma%2Clemmacomp%2Cpos%2Cmsd%2Cdephead%2Cdeprel%2Cref%2Clex%2Cspaces&show_struct=text_title%2Ctext_date%2Ctext_time%2Ctext_author%2Ctext_author_logged_in%2Ctext_author_nick_registered%2Ctext_topic_names%2Ctext_topic_name_top%2Ctext_topic_name_leaf%2Ctext_topic_adultonly%2Ctext_msg_type%2Ctext_empty%2Ctext_id%2Ctext_thread_id%2Ctext_thread_start_datetime%2Ctext_comment_id%2Ctext_parent_comment_id%2Ctext_parent_datetime%2Ctext_quoted_comment_id%2Ctext_filename_vrt%2Cparagraph_type%2Csentence_id%2Csentence_polarity&start=0&end=10000&corpus=CORPUS&cqp=CQP&query_data=&context=&incremental=true&default_within=sentence&within="
  s,year,thread_id = text_id.split("_")
  corpus = s+"_"+year
  cqp = '[ref="1" & _.text_thread_id="'+thread_id+'"]'
  print(cqp)
  url = URL.replace("CORPUS", corpus).replace("CQP", urllib.parse.quote(cqp))
  print(url)
  tmp = wget.download(url)
  with open(tmp, "r", encoding="utf-8") as f:
    data = json.load(f)
  os.remove(tmp)
  res = {}
  for row in data["kwic"]:
    position = row["match"]["position"]
    comment = row["structs"]["text_comment_id"]
    text = " ".join([x["word"] for x in row["tokens"]])
    res[int(position)] = {"comment":comment, "text":text}
  
  res = [res[k] for k in sorted(res.keys())]
  
  for i,x in enumerate(res):
    if i == 0: res_str =  [x["text"]]
    else:
      if x["comment"] != res[i-1]["comment"]: 
        res_str.append("******")
      res_str.append(x["text"])

  return "\n".join(res_str)
