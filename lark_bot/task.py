"""
Main Script
"""

import os
import yaml
import json
import argparse
import datetime
from arxiv_paper import filter_papers_using_llm, prepend_to_json_file, translate_abstracts
from lark_post import post_to_lark_webhook
from lark_table import push_results_to_lark_table
from utils import load_config

def load_and_update_config():
    config = load_config()
    env_mapping = {
        'OPENAI_API_KEY': 'api_key',
        'OPENAI_BASE_URL': 'base_url',
        'MODEL_NAME': 'model',
        'LARK_WEBHOOK_URL': 'webhook_url',
        'LARK_WEBHOOK_SECRET': 'webhook_secret',
        'LARK_TABLE_APP_ID': 'lark_table_app_id',
        'LARK_TABLE_APP_SECRET': 'lark_table_app_secret',
        'LARK_TABLE_BASE_URL': 'lark_table_base_url'
    }
    for env_var, config_key in env_mapping.items():
        env_value = os.environ.get(env_var)
        if env_value:
            config[config_key] = env_value
    return config

# Load Configuration
config = load_and_update_config()
tag = config["tag"]
category_list = config["category_list"]
use_llm_for_filtering = config["use_llm_for_filtering"]
use_llm_for_translation = config["use_llm_for_translation"]

config["base_url"] = os.getenv("OPENAI_BASE_URL")
config["model"] = os.getenv("MODEL_NAME")
config["api_key"] = os.getenv("OPENAI_API_KEY")

paper_file = os.path.join(os.path.dirname(__file__), "papers.json")
if use_llm_for_filtering:
    with open(os.path.join(os.path.dirname(__file__), "paper_to_hunt.md"), "r", encoding="utf-8") as f:
        paper_to_hunt = f.read()

def task(jsonl_path):
    """
    Main task: Fetch Papers & Post to Lark Webhook
    """
    today_date = datetime.date.today().strftime("%Y-%m-%d")
    print("Task: {}".format(today_date))

    papers = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:  # 跳过空行
                papers.append(json.loads(line))
    print("Total papers: {}".format(len(papers)))

    if use_llm_for_filtering:
        papers = filter_papers_using_llm(papers, paper_to_hunt, config)
        print("Filtered papers by LLM: {}".format(len(papers)))

    if use_llm_for_translation:
        papers = translate_abstracts(papers, config)
        print("Translated Abstracts into Chinese")

    # prepend_to_json_file(paper_file, papers)
    # Post to Lark Webhook
    post_to_lark_webhook(tag, papers, config)
    push_results_to_lark_table(papers)


if __name__ == "__main__":
    # Run the task immediately
    parser = argparse.ArgumentParser(description="Fetch and process arXiv papers, or load from JSON Lines file")
    parser.add_argument("--jsonl_path", type=str, help="Path to JSON Lines file containing papers to process")
    args = parser.parse_args()
    task(args.jsonl_path)