"""
Get arXiv papers
"""

import os
import json
import arxiv
from tqdm import tqdm
from llm import is_paper_match, translate_abstract

def deduplicate_papers_across_categories(papers):
    """
    Deduplicate papers across multiple categories
    :param papers: a list of papers
    :return: the deduplicated papers
    """
    # Deduplicate papers while maintaining the order
    # **Note**: Used in the case where multiple categories are involved
    papers_id = set()
    deduplicated_papers = []
    for paper in papers:
        if paper['id'] not in papers_id:
            papers_id.add(paper['id'])
            deduplicated_papers.append(paper)
    return deduplicated_papers


def filter_papers_by_keyword(papers, keyword_list):
    """
    Filter papers by keywords
    :param papers: a list of papers
    :param keyword_list: a list of keywords
    :return: a list of filtered papers
    """
    results = []

    # Below is a less efficient way to filter papers by keywords
    # keyword_list = [keyword.lower() for keyword in keyword_list]
    # for paper in papers:
    #     if any(keyword in paper['summary'].lower() for keyword in keyword_list):
    #         results.append(paper)

    keyword_set = set(keyword.lower() for keyword in keyword_list)
    for paper in papers:
        if keyword_set & set(paper['summary'].lower().split()):
            results.append(paper)

    return results


def filter_papers_using_llm(papers, paper_to_hunt, config: dict):
    """
    Filter papers using LLM
    :param papers: a list of papers
    :param paper_to_hunt: the prompt describing the paper to hunt for
    :param config: the configuration of LLM Server
    :return: a list of filtered papers
    """
    results = []
    for paper in papers:
        if is_paper_match(paper, paper_to_hunt, config):
            results.append(paper)
    return results


def deduplicate_papers(papers, file_path):
    """
    Deduplicate papers according to the previous records
    :param papers: a list of papers
    :param file_path: the file path of the previous records
    :return: the deduplicated papers
    """
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if content:
            content = json.loads(content)
            # Filter out the duplicated papers by id
            content_id = set(d['id'] for d in content)
            papers = [d for d in papers if d['id'] not in content_id]
    # if len(set(d['id'] for d in papers)) == len(papers):
    #     return papers
    return papers


def prepend_to_json_file(file_path, data):
    """
    Prepend data to a JSON file
    :param file_path: the file path
    :param data: the data to prepend
    """
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if content:
            content = json.loads(content)
        else:
            content = []
    else:
        content = []

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data + content, f, indent=4, ensure_ascii=False)


def translate_abstracts(papers: list, config: dict):
    """
    Translate the abstracts using the specified translation service
    :param papers: a list of papers
    :param config: the configuration of LLM Server
    :return: the translated papers
    """
    for paper in tqdm(papers, desc='Translating Abstracts'):
        abstract = paper["summary"]
        zh_abstract = translate_abstract(abstract, config)
        paper["zh_summary"] = None
        if zh_abstract:
            paper["zh_summary"] = zh_abstract
    return papers
