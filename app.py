"""
CloudVar - 云端变量存储 API (Upstash Redis 版本，纯字符串版)

Upstash 免费额度：每天 1 万次请求（约每月 30 万次）

使用前：
1. 访问 https://upstash.com 注册
2. 创建 Redis 数据库
3. 获取 UPSTASH_REDIS_REST_URL 和 UPSTASH_REDIS_REST_TOKEN


from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)


def redis_request(url, token, command, args):
    """发送 Redis REST 请求（通用 GET 调用）"""
    endpoint = f"{url}/{command}/{'/'.join(str(a) for a in args)}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(endpoint, headers=headers)
    return response.json()


def redis_set(url, token, bin_name, key, value):
    """
    设置值（使用 HSET 存储在 hash 中，始终按字符串存储）

    Upstash REST HSET 形如：
    GET  {url}/hset/{key}/{field}/{value}
    这里沿用你原本的 POST 写法，只是取消 JSON 序列化。
    """
    endpoint = f"{url}/HSET/{bin_name}/{key}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    # 不做 json.dumps，直接把字符串发过去
    # 如果 Upstash 那边需要转义，你可以改成 text/plain
    response = requests.post(endpoint, headers=headers, data=value)
    return response.json()


def redis_get(url, token, bin_name, key):
    """获取值（按字符串返回，不做 JSON 解析）"""
    endpoint = f"{url}/HGET/{bin_name}/{key}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(endpoint, headers=headers)
    result = response.json()
    # Upstash 返回形如 {"result": "xxx"}，没有就为 None 或空
    return result.get("result")


def redis_get_all(url, token, bin_name):
    """获取 hash 中所有 key/value（全部按字符串返回）"""
    endpoint = f"{url}/HGETALL/{bin_name}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(endpoint, headers=headers)
    result = response.json()

    data = {}
    items = result.get("result", [])

    # HGETALL 返回 [key1, val1, key2, val2, ...]
    for i in range(0, len(items), 2):
        key = items[i]
        value = items[i + 1]
        data[key] = value

    return data


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
    示例:
    /set?url=REDIS_URL&token=TOKEN&bin_name=mybin&key=date&value=2025-12-06
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
        # 不再尝试解析为 JSON，直接按字符串存储
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
    示例:
    /get?url=REDIS_URL&token=TOKEN&bin_name=mybin&key=date
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
    示例:
    /get_all?url=REDIS_URL&token=TOKEN&bin_name=mybin
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
    示例:
    /delete?url=REDIS_URL&token=TOKEN&bin_name=mybin&key=date
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
        "name": "CloudVar - 云端变量存储 API (Upstash Redis, 纯字符串版)",
        "endpoints": {
            "设置变量": "/set?url=REDIS_URL&token=TOKEN&bin_name=mybin&key=变量名&value=值",
            "获取变量": "/get?url=REDIS_URL&token=TOKEN&bin_name=mybin&key=变量名",
            "获取全部": "/get_all?url=REDIS_URL&token=TOKEN&bin_name=mybin",
            "删除变量": "/delete?url=REDIS_URL&token=TOKEN&bin_name=mybin&key=变量名"
        },
        "说明": "url 和 token 从 https://upstash.com 获取；所有 value 按字符串存取"
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
