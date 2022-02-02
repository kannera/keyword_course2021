import wget
import pandas, numpy
from scipy.stats import binom
import codecs
import os

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

def get_kwic(data, lemma, title, rang):
  indices = data[(data.lemma == lemma) & (data.title==title)].index
  for i in indices:
    line = []
    for ii in range(i-rang, i+rang):
      line.append(data['lemma'].iloc[ii])
    print(" ".join(line))

def build_collocations(data, frequencies, lemma, rang):

  collocations = list_collocations(data, lemma, rang)
  collocations = collocations.groupby('lemma').count()
  tf = data.shape[0]

  collocations['w12'] = collocations['word']
  collocations['w2'] = frequencies
  collocations['tf'] = tf
  collocations['w1'] = frequencies.loc[lemma]
  collocations['pmi'] = collocations.apply(pmi, axis=1)
  collocations['llr'] = collocations.apply(llr, axis=1)
  collocations['t-test'] = collocations.apply(t_test, axis=1)
  return collocations
    
def list_collocations(data, lemma, rang):
  lemma_data = data[data.lemma == lemma]
  texts = lemma_data['text_id'].unique()
  indices = lemma_data.index
  colloc_data = data[data.text_id.isin(texts)]
  set_indices = set(indices)
  max_index = max(data.index)
  colloc_indices = []
  colloc_indices = [list(range(max(0,i-rang), min(i+rang, max_index))) for i in set_indices]
  colloc_indices = list(set([ii for i in colloc_indices for ii in i]))
  return colloc_data[colloc_data.index.isin(colloc_indices)]
    
def build_data_for_collocations(corpus, crop):
  data = get_data_from_github(corpus)
  if crop != "":
    data = data[(data[crop.split(":")[0]] == crop.split(":")[1])]
  frequencies = data.groupby('lemma').count()['word']
  return data, frequencies

def get_data_from_github(corpus):
  if corpus == "coha":
    file_names = ["fic_1.txt","fic_2.txt","mag_1.txt","mag_2.txt","news_1.txt","news_2.txt","nf_1.txt","nf_2.txt"]
    root_path = "https://raw.githubusercontent.com/kannera/keyword_course2021/main/coha/"
    metadata_path = "https://raw.githubusercontent.com/kannera/keyword_course2021/main/coha_metadata.tsv"
    metadata_keys = ['text_id', 'len', 'genre', 'year', 'title', 'author', 'source']
  
  elif corpus == "coca":
    file_names = ["wlp_acad_1.txt","wlp_acad_2.txt","wlp_blog_1.txt","wlp_blog_2.txt","wlp_fic_1.txt","wlp_fic_2.txt","wlp_mag_1.txt","wlp_mag_2.txt","wlp_news_1.txt","wlp_news_2.txt","wlp_spok_1.txt","wlp_spok_2.txt","wlp_tvm_1.txt","wlp_tvm_2.txt","wlp_web_1.txt","wlp_web_2.txt"]
    root_path = "https://raw.githubusercontent.com/kannera/keyword_course2021/main/coca/"
    metadata_path = "https://raw.githubusercontent.com/kannera/keyword_course2021/main/coca_metadata.txt"
    metadata_keys = ["text_id", "year","sub_corpus","len", "source", "title"]
    
  elif corpus == "glowbe":
    file_names = ["au_1.txt","bd_1.txt","ca_1.txt","gb_1.txt","gh_1.txt","hk_1.txt","ie_1.txt","in_1.txt","jm_1.txt","ke_1.txt","lk_1.txt","my_1.txt","ng_1.txt","nz_1.txt","ph_1.txt","pk_1.txt","sg_1.txt","tz_1.txt","us_1.txt","za_1.txt"]
    root_path = "https://raw.githubusercontent.com/kannera/keyword_course2021/main/glowbe/"
    metadata_path = "https://raw.githubusercontent.com/kannera/keyword_course2021/main/glowbe_metadata.tsv"
    metadata_keys = ["text_id", "country|genre", "len", "www-site", "www-page", "title"]

  tmp = wget.download(metadata_path, out="tmp.json")
  with codecs.open(tmp, "r", encoding="utf-8", errors="replace") as f:
    metadata = [x[:-1].split("\t") for x in f]
  os.remove(tmp)
  #os.remove("tmp.json")
  
  metadata = {x[0]:{metadata_keys[i]:x[i] for i in range(1, len(metadata_keys))} for x in metadata}

  print("this done")
  data = []
  for fn in file_names:
    tmp = wget.download(root_path+fn, out="tmp.json")
    with codecs.open(tmp, "r", encoding="utf-8", errors="replace") as f:
      data.extend([x[:-1].replace("@@","").split("\t") for x in f])
    #os.remove("tmp.json")
    os.remove(tmp)

  df = pandas.DataFrame(data)
  
  df.columns = [x for x in ["text_id", "word", "lemma", "x1", "x2"][:df.shape[1]]]
  
  for key in metadata_keys[1:]:
    df[key] = df["text_id"].apply(lambda x:metadata[x][key])


  return df
