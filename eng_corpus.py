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
  #print(metadata)
  metadata = {x[0]:{metadata_keys[i]:x[i] for i in range(1, len(metadata_keys))} for x in metadata}

  print("this done")
  data = []
  for fn in file_names:
    tmp = wget.download(root_path+fn, out="tmp.json")
    with codecs.open(tmp, "r", encoding="utf-8", errors="replace") as f:
      data.extend([x[:-1].replace("@@","").split("\t") for x in f])

  df = pandas.DataFrame(data)
  print(df)
  df.columns = [x for x in ["text_id", "word", "lemma", "x1", "x2"][:df.shape[1]]]
  print(df)
  for key in metadata_keys[1:]:
    df[key] = df["text_id"].apply(lambda x:metadata[x][key])


  return df
