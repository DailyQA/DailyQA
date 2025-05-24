
import json
import argparse
from tqdm import tqdm
from pywikibot import Timestamp
from multiprocessing import Pool
import pywikibot
import time
import mwparserfromhell


def clean_wikinode(parsed):
    new_parsed = mwparserfromhell.wikicode.Wikicode([])
    to_remove = []
    for tag in parsed.filter_tags():
        # print(tag.tag)
        # print(str(tag))
        if tag.tag == 'ref':
        #     # print(tag)
            to_remove.append(str(tag))
    for node in parsed.nodes:
        # print(str(node))
        # print(type(node))
        if str(node) not in to_remove:
            # print(str(node))
            new_parsed.append(node)
        # else:
            # print(str(node))
            # new_parsed.append(" ")

    return new_parsed


def my_parse_infobox(wiki_str):
    t1 = time.time()
    parsed = mwparserfromhell.parse(wiki_str)
    t2 = time.time()
    
    inforboxs = []
    templates = parsed.filter_templates()

    # for template in templates:
    #     print(type(template))
    #     print("模板名称:", template.name)
    #     for param in template.params:
    #         print(f"  参数: {param.name} = {param.value}")
    for template in templates:
        if template.name.strip().lower().startswith("infobox"):
            inforboxs.append(template)
    
    info_strs = []
    infoboxes = []
    for inforbox in inforboxs:
        # info_str = str(inforbox)
        para_strs = []
        infobox = dict()
        for param in inforbox.params:
            name = param.name.strip()
            value = clean_wikinode(param.value).strip_code().strip()
            para_strs.append(f"{name}: {value}")
            infobox[name] = value
        # info_str = "\n".join([f"{t.name.strip()}: {t.value.strip_code().strip()}" for t in inforbox.params])
        info_str = "\n".join(para_strs)
        info_strs.append(info_str)
        infoboxes.append(infobox)

    infos = "\n\n".join(info_strs)

    return infos, infoboxes, None


def get_page_specifying_time(title, timestamp):
    site = pywikibot.Site("en", "wikipedia")
    page = pywikibot.Page(site, title)
    revisions = page.revisions()
    # sorted_revs = sorted(list(revisions), key=lambda x: x['timestamp'], reverse=True)
    selected_rev = None
    for revision in revisions:
    # 如果该修订时间戳小于或等于指定的时间戳
        if revision['timestamp'] <= timestamp:
            selected_rev = revision
            break
            # return revision
    try:
        text = page.getOldVersion(selected_rev['revid'], force=True)
    except Exception as e:
        # print(f"\nrevisions: {list(revisions)}")
        raise e
    return text

def get_answer(wiki_page, stand_infobox, infobox_key):
    text, infoboxes, templates = my_parse_infobox(wiki_page)
    stand_keys = set(stand_infobox.keys())

    target_infobox = {}
    for infobox in infoboxes:
        tmp_set = set(infobox.keys())
        intersec = stand_keys.intersection(tmp_set)
        if len(intersec) > len(stand_keys)/2 and infobox_key in tmp_set: 
            answer = infobox[infobox_key]
            return answer
    return None

def query_format(data, answer):
    new_data = {}
    new_data["id"] = data["id"]
    new_data["query"] = data["query"]
    new_data["answer"] = answer

    return new_data

def get_new_data(data, timestamp):
    retry = 5
    while retry > 0:
        try:
            title = data["title"]
            wiki_page = get_page_specifying_time(title, timestamp)
            answer = get_answer(wiki_page, data["new_block"], data["entity_name"])
            new_data = query_format(data, answer)
            return new_data
        except Exception as e:
            retry -= 1
            print(f"Error {e}\nLeft retry: {retry}")
            # print(data["id"])
            # raise e
            if retry == 0:
                answer = None
                new_data = query_format(data, answer)
                return new_data



def processing_data(args):
    return get_new_data(*args)

def download_answers(query_path, out_path, timestamp):
    fout = open(out_path, "w")
    ids = []
    datas_ts = []
    with open(query_path) as fin:
        for line in tqdm(fin):
            data = json.loads(line)
            datas_ts.append((data, timestamp))
            ids.append(data["id"])

    with Pool(20) as pool:
        results = pool.imap_unordered(processing_data, datas_ts)
        for result in tqdm(results):
            fout.write(json.dumps(result, ensure_ascii=False) + "\n")
            fout.flush()
    fout.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--query_name", type=str, required=True, help="query path")
    parser.add_argument("--qa_name", type=str, required=True, help="qa path")
    parser.add_argument("--search_day", type=str, default="now", help="which day")
    args = parser.parse_args()
    
    search_day = args.search_day
    year = int("20" + search_day[0:2])
    month = int(search_day[2:4])
    date = int(search_day[4:6])
    timestamp = Timestamp(year,month,date,0,0,0)

    query_path = f"data/query/{args.query_name}.jsonl"
    out_path = f"data/qa/{args.qa_name}.jsonl"
    
    download_answers(query_path, out_path, timestamp)

