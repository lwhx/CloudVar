# 云端变量存储 API

通过 URL 参数设置和获取云端变量。

## 部署到 Zeabur

### 方法一：通过 GitHub 部署（推荐）

1. 将此文件夹上传到 GitHub 仓库
2. 登录 [Zeabur](https://zeabur.com)
3. 创建新项目 → 选择 "Deploy from GitHub"
4. 选择你的仓库
5. Zeabur 会自动识别 Python 项目并部署
6. 部署完成后，在 "Networking" 中生成域名

### 方法二：通过 Zeabur CLI 部署

```bash
# 安装 CLI
npm install -g @zeabur/cli

# 登录
zeabur login

# 部署
zeabur deploy
```

## API 使用

部署后，假设你的域名是 `https://cloud-var.zeabur.app`

### 设置变量
```
https://cloud-var.zeabur.app/set?api_key=YOUR_KEY&bin_name=mybin&key=日期&value=2025-12-05
```

### 获取变量
```
https://cloud-var.zeabur.app/get?api_key=YOUR_KEY&bin_name=mybin&key=日期
```

### 获取所有变量
```
https://cloud-var.zeabur.app/get_all?api_key=YOUR_KEY&bin_name=mybin
```

### 删除变量
```
https://cloud-var.zeabur.app/delete?api_key=YOUR_KEY&bin_name=mybin&key=日期
```

## 参数说明

| 参数 | 说明 |
|------|------|
| api_key | JSONBin.io 的 API 密钥，在 https://jsonbin.io 注册获取 |
| bin_name | 存储空间名称，相同名称共享数据 |
| key | 变量名 |
| value | 变量值（支持字符串、数字、JSON） |

## 返回示例

```json
// 设置成功
{
  "success": true,
  "action": "创建",
  "key": "日期",
  "value": "2025-12-05"
}

// 获取成功
{
  "success": true,
  "key": "日期",
  "value": "2025-12-05"
}

// 获取全部
{
  "success": true,
  "variables": {
    "日期": "2025-12-05",
    "name": "test"
  },
  "count": 2
}
```

## 文件结构

```
├── app.py              # 主程序
├── requirements.txt    # Python 依赖
├── Procfile           # 启动配置
└── README.md          # 说明文档
```
