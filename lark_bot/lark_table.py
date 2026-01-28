import os
import sys
import json
import time
import requests
import urllib.parse
from typing import Dict, Any, Tuple, Optional


def get_tenant_access_token(app_id: str, app_secret: str) -> Tuple[str, Exception]:
    """获取 tenant_access_token

    Args:
        app_id: 应用ID
        app_secret: 应用密钥

    Returns:
        Tuple[str, Exception]: (access_token, error)
    """
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = {
        "app_id": app_id,
        "app_secret": app_secret
    }
    headers = {
        "Content-Type": "application/json; charset=utf-8"
    }
    try:
        print(f"POST: {url}")
        print(f"Request payload: {json.dumps(payload)}")
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()

        result = response.json()
        print(f"Response: {json.dumps(result)}")

        if result.get("code", 0) != 0:
            print(f"ERROR: failed to get tenant_access_token: {result.get('msg', 'unknown error')}", file=sys.stderr)
            return "", Exception(f"failed to get tenant_access_token: {response.text}")

        return result["tenant_access_token"], None

    except Exception as e:
        print(f"ERROR: getting tenant_access_token: {e}", file=sys.stderr)
        if hasattr(e, 'response') and e.response is not None:
            print(f"ERROR: Response text: {e.response.text}", file=sys.stderr)
        return "", e

def get_wiki_node_info(tenant_access_token: str, node_token: str) -> Dict[str, Any]:
    """获取知识空间节点信息

    Args:
        tenant_access_token: 租户访问令牌
        node_token: 节点令牌

    Returns:
        Dict[str, Any]: 节点信息对象
    """
    url = f"https://open.feishu.cn/open-apis/wiki/v2/spaces/get_node?token={urllib.parse.quote(node_token)}"
    headers = {
        "Authorization": f"Bearer {tenant_access_token}",
        "Content-Type": "application/json; charset=utf-8"
    }

    try:
        print(f"GET: {url}")
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        result = response.json()
        if result.get("code", 0) != 0:
            print(f"ERROR: 获取知识空间节点信息失败 {result}", file=sys.stderr)
            raise Exception(f"failed to get wiki node info: {result.get('msg', 'unknown error')}")

        if not result.get("data") or not result["data"].get("node"):
            raise Exception("未获取到节点信息")

        node_info = result["data"]["node"]
        print("节点信息获取成功:", {
            "node_token": node_info.get("node_token"),
            "obj_type": node_info.get("obj_type"),
            "obj_token": node_info.get("obj_token"),
            "title": node_info.get("title")
        })
        return node_info

    except Exception as e:
        print(f"Error getting wiki node info: {e}", file=sys.stderr)
        raise

def parse_base_url(tenant_access_token: str, base_url_string: str) -> Dict[str, Optional[str]]:
    """解析多维表格参数

    Args:
        tenant_access_token: 租户访问令牌
        base_url_string: 基础URL字符串

    Returns:
        Dict[str, Optional[str]]: 包含appToken、tableID、viewID的字典
    """
    from urllib.parse import urlparse, parse_qs

    parsed_url = urlparse(base_url_string)
    pathname = parsed_url.path
    app_token = pathname.split("/")[-1]

    if "/wiki/" in pathname:
        node_info = get_wiki_node_info(tenant_access_token, app_token)
        app_token = node_info.get("obj_token", app_token)

    query_params = parse_qs(parsed_url.query)
    view_id = query_params.get("view", [None])[0]
    table_id = query_params.get("table", [None])[0]

    return {
        "app_token": app_token,
        "table_id": table_id,
        "view_id": view_id
    }

def create_bitable_record(tenant_access_token: str, app_token: str, table_id: str, fields: Dict[str, Any], user_id_type: str = "open_id") -> Tuple[Dict[str, Any], Exception]:
    """在多维表格中新增一条记录

    Args:
        tenant_access_token: 租户访问令牌
        app_token: 多维表格app token
        table_id: 数据表ID
        fields: 要新增的记录数据,key为字段名称,value为字段值
        user_id_type: 用户ID类型,默认为open_id

    Returns:
        Tuple[Dict[str, Any], Exception]: (响应数据, 错误)
    """
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records"
    
    # 构建查询参数
    params = {
        "user_id_type": user_id_type
    }
    
    headers = {
        "Authorization": f"Bearer {tenant_access_token}",
        "Content-Type": "application/json; charset=utf-8"
    }
    
    # 构建请求体
    payload = {
        "fields": fields
    }
    
    try:
        print(f"POST: {url}")
        print(f"Query params: {json.dumps(params)}")
        print(f"Request body: {json.dumps(payload, ensure_ascii=False)}")
        
        response = requests.post(url, params=params, json=payload, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        print(f"Response: {json.dumps(result, ensure_ascii=False)}")
        
        if result.get("code", 0) != 0:
            print(f"ERROR: 新增记录失败: {result.get('msg', 'unknown error')}", file=sys.stderr)
            return {}, Exception(f"failed to create record: {response.text}")
            
        return result, None
        
    except Exception as e:
        print(f"ERROR: creating bitable record: {e}", file=sys.stderr)
        if hasattr(e, 'response') and e.response is not None:
            print(f"ERROR: Response text: {e.response.text}", file=sys.stderr)
        return {}, e

def push_results_to_lark_table(papers):
    app_id = os.getenv("LARK_TABLE_APP_ID")
    app_secret = os.getenv("LARK_TABLE_APP_SECRET")
    base_url = os.getenv("LARK_TABLE_BASE_URL")
    user_id_type = os.getenv("USER_ID_TYPE", "open_id")
    for paper in papers:
        fields_data = {
            "Title": paper["title"], 
            "Link": {
                "text": paper["pdf"], 
                "link": paper["pdf"]
            },
            "Date": time.time() * 1000,
            "Summary": paper.get("zh_summary", None),
        }
        # 获取 tenant_access_token
        tenant_access_token, err = get_tenant_access_token(app_id, app_secret)
        if err:
            print(f"ERROR: getting tenant_access_token: {err}", file=sys.stderr)
            exit(1)
        # 解析多维表格参数
        try:
            bitable_info = parse_base_url(tenant_access_token, base_url)
            app_token = bitable_info["app_token"]
            table_id = bitable_info["table_id"]
            
            if not app_token:
                print("ERROR: 无法获取 app_token", file=sys.stderr)
                exit(1)
            if not table_id:
                print("ERROR: 无法获取 table_id,请确保URL中包含table参数", file=sys.stderr)
                exit(1)
            print(f"解析多维表格参数成功: app_token={app_token}, table_id={table_id}")
        except Exception as e:
            print(f"ERROR: 解析多维表格参数失败: {e}", file=sys.stderr)
            exit(1)
        # 新增记录
        result, err = create_bitable_record(tenant_access_token, app_token, table_id, fields_data, user_id_type)
        if err:
            print(f"ERROR: 新增记录失败: {err}", file=sys.stderr)
            exit(1)
        # 输出成功信息
        record_id = result.get("data", {}).get("record", {}).get("record_id", "")
        if record_id:
            print(f"新增记录成功,记录ID: {record_id}")
        else:
            print("新增记录成功,但未返回记录ID")
    print("操作完成")