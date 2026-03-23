# 猿人学爬虫逆向 - 第一题解决方案

猿人学平台反爬虫挑战第一题的 Python 解决方案。

## 项目结构

```
yuanrenxue/
├── yuanrenxue_solution_1.py   # 主要解决方案脚本
├── yuanrenxue_test_v3.py      # 测试脚本 v3
├── yuanrenxue_test_v4.py      # 测试脚本 v4
└── README.md
```

## 核心发现

1. **m 参数格式**: `{MD5_hash}丨{timestamp/1000}`
2. **MD5_hash**: 由混淆的 `hex_md5(timestamp)` 生成，与标准 MD5 不同
3. **timestamp**: `Date.now() + 100000000` (毫秒)
4. **window.a**: 经过 `XOR(c=5)` -> `base64` 解码得到 JS 代码
5. **服务器验证**: 使用混淆的 MD5 进行验证

## 解决方案

### 方式一：通过 CDP 获取 m 参数 (推荐)

使用浏览器 CDP 接口获取实时的 `m` 参数和 `sessionid`，立即发送 API 请求。

**前置条件**:
- 需要运行 [Clash verge](https://github.com/Clash-verge/Clash-Verge) 或类似的 CDP 服务（默认端口 3456）
- 浏览器需要打开目标页面 `https://match.yuanrenxue.cn/match/1`

**运行**:
```bash
python yuanrenxue_solution_1.py
```

**结果**:
```
========================================
结果: 50 个数字
总和: 29429667
========================================
```

### 方式二：通过页面提取 window.a

从页面 HTML 中提取 `window.a`，解码获取 MD5 算法，生成 m 参数。

**运行**:
```bash
python yuanrenxue_test_v3.py
```

## API 请求说明

### Page 1-4
- **URL**: `https://match.yuanrenxue.cn/api/question/1`
- **Method**: GET
- **参数**: `page={页码}&m={m参数}`
- **Headers**:
  - `User-Agent`: 标准浏览器 UA
  - `Cookie`: `sessionid={sessionid}`

### Page 5
- **URL**: `https://match.yuanrenxue.cn/api/question/1`
- **Method**: GET
- **参数**: `page=5&m={m参数}`
- **Headers**:
  - `User-Agent`: `yuanrenxue`
  - `Cookie`: `sessionid={sessionid}`

## 技术栈

- Python 3
- urllib.request (内置)
- hashlib (内置)
- CDP (Chrome DevTools Protocol)
