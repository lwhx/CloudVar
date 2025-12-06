"""
CloudVar - 云端变量存储 API (Upstash Redis 版本)

Upstash 免费额度：每天 1 万次请求（约每月 30 万次）

使用前：
1. 访问 https://upstash.com 注册
2. 创建 Redis 数据库
3. 获取 UPSTASH_REDIS_REST_URL 和 UPSTASH_REDIS_REST_TOKEN
"""

from flask import Flask, request, jsonify
import requests
import json
import os

app = Flask(__name__)


def redis_request(url, token, command, args):
    """发送 Redis REST 请求"""
    endpoint = f"{url}/{command}/{'/'.join(str(a) for a in args)}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(endpoint, headers=headers)
    return response.json()


def redis_set(url, token, bin_name, key, value):
    """设置值（使用 HSET 存储在 hash 中）"""
    endpoint = f"{url}/HSET/{bin_name}/{key}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    # 将值转为 JSON 字符串存储
    response = requests.post(endpoint, headers=headers, data=json.dumps(value))
    return response.json()


def redis_get(url, token, bin_name, key):
    """获取值"""
    endpoint = f"{url}/HGET/{bin_name}/{key}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(endpoint, headers=headers)
    result = response.json()
    if result.get("result"):
        try:
            return json.loads(result["result"])
        except:
            return result["result"]
    return None


def redis_get_all(url, token, bin_name):
    """获取所有值"""
    endpoint = f"{url}/HGETALL/{bin_name}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(endpoint, headers=headers)
    result = response.json()
    
    if result.get("result"):
        data = {}
        items = result["result"]
        # HGETALL 返回 [key1, val1, key2, val2, ...]
        for i in range(0, len(items), 2):
            key = items[i]
            try:
                value = json.loads(items[i + 1])
            except:
                value = items[i + 1]
            data[key] = value
        return data
    return {}


def redis_delete(url, token, bin_name, key):
    """删除值"""
    endpoint = f"{url}/HDEL/{bin_name}/{key}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(endpoint, headers=headers)
    result = response.json()
    return result.get("result", 0) > 0


def redis_exists(url, token, bin_name, key):
    """检查 key 是否存在"""
    endpoint = f"{url}/HEXISTS/{bin_name}/{key}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(endpoint, headers=headers)
    result = response.json()
    return result.get("result", 0) == 1


@app.route("/set", methods=["GET", "POST"])
def set_variable():
    """
    设置变量
    参数: url, token, bin_name, key, value
    """
    redis_url = request.args.get("url")
    token = request.args.get("token")
    bin_name = request.args.get("bin_name")
    key = request.args.get("key")
    value = request.args.get("value")
    
    if not all([redis_url, token, bin_name, key, value]):
        return jsonify({
            "success": False,
            "error": "缺少参数，需要: url, token, bin_name, key, value"
        }), 400
    
    try:
        # 尝试解析 value 为 JSON
        try:
            value = json.loads(value)
        except:
            pass
        
        # 检查是否已存在
        is_new = not redis_exists(redis_url, token, bin_name, key)
        
        # 设置值
        redis_set(redis_url, token, bin_name, key, value)
        
        return jsonify({
            "success": True,
            "action": "创建" if is_new else "修改",
            "key": key,
            "value": value
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/get", methods=["GET"])
def get_variable():
    """
    获取变量
    参数: url, token, bin_name, key
    """
    redis_url = request.args.get("url")
    token = request.args.get("token")
    bin_name = request.args.get("bin_name")
    key = request.args.get("key")
    
    if not all([redis_url, token, bin_name, key]):
        return jsonify({
            "success": False,
            "error": "缺少参数，需要: url, token, bin_name, key"
        }), 400
    
    try:
        value = redis_get(redis_url, token, bin_name, key)
        
        if value is not None:
            return jsonify({
                "success": True,
                "key": key,
                "value": value
            })
        else:
            return jsonify({
                "success": False,
                "error": f"变量 '{key}' 不存在"
            }), 404
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/get_all", methods=["GET"])
def get_all_variables():
    """
    获取所有变量
    参数: url, token, bin_name
    """
    redis_url = request.args.get("url")
    token = request.args.get("token")
    bin_name = request.args.get("bin_name")
    
    if not all([redis_url, token, bin_name]):
        return jsonify({
            "success": False,
            "error": "缺少参数，需要: url, token, bin_name"
        }), 400
    
    try:
        data = redis_get_all(redis_url, token, bin_name)
        
        return jsonify({
            "success": True,
            "variables": data,
            "count": len(data)
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/delete", methods=["GET", "POST"])
def delete_variable():
    """
    删除变量
    参数: url, token, bin_name, key
    """
    redis_url = request.args.get("url")
    token = request.args.get("token")
    bin_name = request.args.get("bin_name")
    key = request.args.get("key")
    
    if not all([redis_url, token, bin_name, key]):
        return jsonify({
            "success": False,
            "error": "缺少参数，需要: url, token, bin_name, key"
        }), 400
    
    try:
        if redis_delete(redis_url, token, bin_name, key):
            return jsonify({
                "success": True,
                "action": "删除",
                "key": key
            })
        else:
            return jsonify({
                "success": False,
                "error": f"变量 '{key}' 不存在"
            }), 404
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "name": "CloudVar - 云端变量存储 API (Upstash Redis)",
        "endpoints": {
            "设置变量": "/set?url=REDIS_URL&token=TOKEN&bin_name=mybin&key=变量名&value=值",
            "获取变量": "/get?url=REDIS_URL&token=TOKEN&bin_name=mybin&key=变量名",
            "获取全部": "/get_all?url=REDIS_URL&token=TOKEN&bin_name=mybin",
            "删除变量": "/delete?url=REDIS_URL&token=TOKEN&bin_name=mybin&key=变量名"
        },
        "说明": "url 和 token 从 https://upstash.com 获取"
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
