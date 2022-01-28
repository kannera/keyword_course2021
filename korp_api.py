URL_COM = "https://korp.csc.fi/cgi-bin/korp/korp.cgi?command=COMMAND&defaultcontext=1+sentence&cache=true"
URL_GROUPBY = "groupby=GROUPBY"
URL_SHOW = "show=sentence.paragraph.lemma(.comp).pos.msd.dep(head.rel).ref"
URL_STRUCT_KLK = "show_struct=text_label.text_publ_(title.id).text_issue_(date.no.title).text_(elec_date.language.page_no.sentcount.tokencount.img_url.publ_type).paragraph_id.sentence_(id.parse_state.local_id).text_binding_id.text_page_image_(url.context_url).text_download_pdf_url"
URL_START_END = "&start=START&end=END"
URL_CORPUS_KLK = "corpus=KLK_FI_18(99.98.97.96.95.94.93.92.91.90.89.88.87.86.85.84.83.82.81.80.79.78.77.76.75.74.73.72.71.70.69.68.67.66.65.64.63.62.61.60)
URL_ENDBITS =  "context=&incremental=true&defaultwithin=sentence&within=&loginfo=lang%3Dfi+search%3Dadv"
URL_QUERY = "cqp=QUERY"

def query_frequencies(lemma, groupby):
  url = "&".join([URL_COM.replace("COMMAND", "count"), URL_GROUPBY.replace("GROUPBY", groupby), URL_CORPUS_KLK, URL_QUERY.replace(QUERY, '[lemma="'+lemma+'"]'), URL_ENDBITS])
  !wget $url -O tmp.json
  with open("tmp.json", "r", encoding="utf-8") as f:
    data = json.load(f)
  print(data.keys())