# CloudVar - 云端变量存储 (Upstash Redis 版)

免费额度：每天 1 万次请求（约每月 30 万次）

## 获取 Upstash 凭证

1. 访问 https://upstash.com 注册（支持 GitHub 登录）
2. 点击 "Create Database"
3. 选择区域（推荐选离你近的）
4. 创建后，在 "REST API" 部分找到：
   - `UPSTASH_REDIS_REST_URL`（类似 https://xxx.upstash.io）
   - `UPSTASH_REDIS_REST_TOKEN`

## API 使用

### 设置变量
```
/set?url=YOUR_URL&token=YOUR_TOKEN&bin_name=mybin&key=日期&value=2025-12-05
```

### 获取变量
```
/get?url=YOUR_URL&token=YOUR_TOKEN&bin_name=mybin&key=日期
```

### 获取所有变量
```
/get_all?url=YOUR_URL&token=YOUR_TOKEN&bin_name=mybin
```

### 删除变量
```
/delete?url=YOUR_URL&token=YOUR_TOKEN&bin_name=mybin&key=日期
```

## 参数说明

| 参数 | 说明 |
|------|------|
| url | Upstash REST URL |
| token | Upstash REST Token |
| bin_name | 存储空间名称（相同名称共享数据） |
| key | 变量名 |
| value | 变量值 |

## 部署到 Zeabur

1. 上传到 GitHub
2. 在 Zeabur 创建项目，选择 GitHub 仓库
3. 自动部署完成后生成域名
