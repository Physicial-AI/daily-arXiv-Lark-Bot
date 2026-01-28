"""
LLM Utilities
"""

import re
from utils import get_llm_response


def is_paper_match(paper: dict, paper_to_hunt: str, config: dict) -> bool:
    """
    Check if the paper matches `paper_to_hunt` description using LLM
    :param paper: the paper to check
    :param paper_to_hunt: the prompt describing the paper to hunt for
    :param config: the configuration of LLM Server
    :return: True if the paper matches or LLM Service fails, False otherwise
    """
    paper_title = paper['title']
    paper_abstract = paper['summary']
    prompt = f'你是一个专业的学术论文筛选助手。你的任务是判断给定的论文是否符合我正在寻找的研究内容。\n\n请仔细阅读以下论文的标题和摘要：\n标题：{paper_title}\n摘要：{paper_abstract}\n\n我正在寻找的研究内容(paper_to_hunt)：\n{paper_to_hunt}\n\n---\n\n请分析这篇论文的内容是否与我寻找的研究内容相符。在分析时，请考虑：\n1. 研究主题的相关性\n2. 论文的关键概念与我的研究描述的匹配程度\n\n基于你的分析，如果这篇论文符合我要找的研究内容，请只回答"Yes"；如果不符合，请只回答"No"。'
    response = get_llm_response(prompt, config)
    if not response:
        # LLM Service Error, assuming the paper matches
        print('LLM Service Error for paper: {}. Assuming it matches.'.format(paper_title))
        return True

    # Filter out the thinking process wrapped between <think> and </think> (if any)
    response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL).strip()
    print('LLM response for paper "{}": {}'.format(paper_title, response))

    # if 'yes' in response.lower() and 'no' in response.lower():
    #     print('LLM returned ambiguous response for paper: {}.\nResponse: {}'.format(paper_title, response))
    #     return True

    # if 'yes' in response.lower():
    #     return True
    # if 'no' in response.lower():
    #     return False

    # print('LLM returned unexpected response for paper: {}.\nResponse: {}'.format(paper_title, response))
    # return False

    # If logging is not needed, it can be simplified as below
    return 'yes' in response.lower()


def translate_abstract(abstract: str, config: dict):
    """
    Translate the abstract using LLM
    :param abstract: the abstract to translate
    :param config: the configuration of LLM Server
    :return: the translated abstract or None if failed
    """
    prompt = f'请将下面的学术论文摘要翻译为中文：\n{abstract}\n\n**注意**：\n- 中文语境中常用的英文学术术语可以保留英文原文，如：自然语言处理中的 Transformer 可以保留英文。\n- 其他关键的学术术语可以中英文对照，如：后门攻击(Backdoor Attack)。\n- 直接给出翻译结果，不需要进行解释，不需要任何其他内容。'
    translated_text = get_llm_response(prompt, config)
    if not translated_text:
        return None
    # Filter out the thinking process wrapped between <think> and </think> (if any)
    translated_text = re.sub(r'<think>.*?</think>', '', translated_text, flags=re.DOTALL)
    return translated_text.strip()
