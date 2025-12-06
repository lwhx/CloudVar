"""
CloudVar - 云端变量存储 API
"""

from flask import Flask, request, jsonify
import requests
import json
import os

app = Flask(__name__)

BIN_CACHE = {}


def get_or_create_bin(api_key, bin_name):
    """获取或创建 bin"""
    cache_key = f"{api_key}:{bin_name}"
    
    if cache_key in BIN_CACHE:
        return BIN_CACHE[cache_key]
    
    bin_id = find_bin_by_name(api_key, bin_name)
    if bin_id:
        BIN_CACHE[cache_key] = bin_id
        return bin_id
    
    url = "https://api.jsonbin.io/v3/b"
    headers = {
        "Content-Type": "application/json",
        "X-Master-Key": api_key,
        "X-Bin-Name": bin_name
    }
    response = requests.post(url, json={}, headers=headers)
    
    if response.status_code == 200:
        bin_id = response.json()["metadata"]["id"]
        BIN_CACHE[cache_key] = bin_id
        return bin_id
    else:
        raise Exception(f"创建 Bin 失败: {response.text}")


def find_bin_by_name(api_key, bin_name):
    """通过名称查找已存在的 bin"""
    url = "https://api.jsonbin.io/v3/c/uncategorized/bins"
    headers = {"X-Master-Key": api_key}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            bins = response.json()
            for bin_info in bins:
                if bin_info.get("snippetMeta", {}).get("name") == bin_name:
                    return bin_info["record"]
    except:
        pass
    return None


def get_all_data(api_key, bin_id):
    """获取 bin 中所有数据"""
    url = f"https://api.jsonbin.io/v3/b/{bin_id}/latest"
    headers = {"X-Master-Key": api_key}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()["record"]
    return {}


def save_data(api_key, bin_id, data):
    """保存数据到 bin"""
    url = f"https://api.jsonbin.io/v3/b/{bin_id}"
    headers = {
        "Content-Type": "application/json",
        "X-Master-Key": api_key
    }
    response = requests.put(url, json=data, headers=headers)
    return response.status_code == 200


@app.route("/set", methods=["GET", "POST"])
def set_variable():
    api_key = request.args.get("api_key")
    bin_name = request.args.get("bin_name")
    key = request.args.get("key")
    value = request.args.get("value")
    
    if not all([api_key, bin_name, key, value]):
        return jsonify({
            "success": False,
            "error": "缺少参数，需要: api_key, bin_name, key, value"
        }), 400
    
    try:
        try:
            value = json.loads(value)
        except:
            pass
        
        bin_id = get_or_create_bin(api_key, bin_name)
        data = get_all_data(api_key, bin_id)
        
        is_new = key not in data
        data[key] = value
        
        if save_data(api_key, bin_id, data):
            return jsonify({
                "success": True,
                "action": "创建" if is_new else "修改",
                "key": key,
                "value": value
            })
        else:
            return jsonify({"success": False, "error": "保存失败"}), 500
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/get", methods=["GET"])
def get_variable():
    api_key = request.args.get("api_key")
    bin_name = request.args.get("bin_name")
    key = request.args.get("key")
    
    if not all([api_key, bin_name, key]):
        return jsonify({
            "success": False,
            "error": "缺少参数，需要: api_key, bin_name, key"
        }), 400
    
    try:
        bin_id = get_or_create_bin(api_key, bin_name)
        data = get_all_data(api_key, bin_id)
        
        if key in data:
            return jsonify({
                "success": True,
                "key": key,
                "value": data[key]
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
    api_key = request.args.get("api_key")
    bin_name = request.args.get("bin_name")
    
    if not all([api_key, bin_name]):
        return jsonify({
            "success": False,
            "error": "缺少参数，需要: api_key, bin_name"
        }), 400
    
    try:
        bin_id = get_or_create_bin(api_key, bin_name)
        data = get_all_data(api_key, bin_id)
        
        return jsonify({
            "success": True,
            "variables": data,
            "count": len(data)
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/delete", methods=["GET", "POST"])
def delete_variable():
    api_key = request.args.get("api_key")
    bin_name = request.args.get("bin_name")
    key = request.args.get("key")
    
    if not all([api_key, bin_name, key]):
        return jsonify({
            "success": False,
            "error": "缺少参数，需要: api_key, bin_name, key"
        }), 400
    
    try:
        bin_id = get_or_create_bin(api_key, bin_name)
        data = get_all_data(api_key, bin_id)
        
        if key in data:
            del data[key]
            if save_data(api_key, bin_id, data):
                return jsonify({
                    "success": True,
                    "action": "删除",
                    "key": key
                })
        
        return jsonify({
            "success": False,
            "error": f"变量 '{key}' 不存在"
        }), 404
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "name": "CloudVar - 云端变量存储 API",
        "endpoints": {
            "设置变量": "/set?api_key=xxx&bin_name=mybin&key=变量名&value=值",
            "获取变量": "/get?api_key=xxx&bin_name=mybin&key=变量名",
            "获取全部": "/get_all?api_key=xxx&bin_name=mybin",
            "删除变量": "/delete?api_key=xxx&bin_name=mybin&key=变量名"
        },
        "说明": "api_key 从 https://jsonbin.io 获取"
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
