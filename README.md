# 猿人学爬虫逆向 - 解决方案

猿人学平台反爬虫挑战的 Python 解决方案。

## 项目结构

```
yuanrenxue/
├── yuanrenxue_solution_1.py   # 第一题解决方案
├── yuanrenxue_solution_2.py   # 第二题解决方案
├── yuanrenxue_test_v3.py     # 测试脚本 v3
├── yuanrenxue_test_v4.py     # 测试脚本 v4
└── README.md
```

## 第一题 - 动态cookie与混淆MD5

### 核心发现

1. **m 参数格式**: `{MD5_hash}丨{timestamp/1000}`
2. **MD5_hash**: 由混淆的 `hex_md5(timestamp)` 生成，与标准 MD5 不同
3. **timestamp**: `Date.now() + 100000000` (毫秒)
4. **window.a**: 经过 `XOR(c=5)` -> `base64` 解码得到 JS 代码
5. **服务器验证**: 使用混淆的 MD5 进行验证

### 解决方案

使用浏览器 CDP 接口获取实时的 `m` 参数和 `sessionid`，立即发送 API 请求。

**前置条件**:
- 需要运行 Clash verge 或类似的 CDP 服务（默认端口 3456）
- 浏览器需要打开目标页面

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

## 第二题 - js 混淆与动态cookie

### 核心发现

1. **m 参数格式**: `{MD5_hash}|{timestamp}`
2. **m 参数存储在 cookie 中**，自动发送到服务器
3. **API 返回混淆的 JS 代码**：需要在浏览器中 eval 执行后再次请求才能获取真实数据
4. **第5页验证**：需要将 User-Agent 修改为 `yuanrenxue`，但服务器有额外的 TLS/HTTP2 指纹检测

### 解决方案

通过 CDP 点击页面按钮触发 AJAX 请求获取数据。

**前置条件**:
- 需要运行 CDP 服务（默认端口 3456）
- 浏览器需要打开目标页面

**运行**:
```bash
python yuanrenxue_solution_2.py
```

**结果 (Page 1-4)**:
```
Page 1: [789942, 321551, 179202, 179203, 920487, 903432, 371753, 774357, 661655, 116650]
Page 2: [904136, 822211, 159409, 894938, 174825, 972182, 468643, 533066, 176049, 739265]
Page 3: [253390, 309611, 199986, 517848, 704728, 556590, 596554, 244703, 470395, 717126]
Page 4: [451362, 304594, 319659, 873438, 198792, 526391, 766310, 153733, 404163, 283562]

已获取: 40 个数字
总和: 19915891
```

**注意**: 第5页需要特殊的 User-Agent (`yuanrenxue`)，但服务器有额外的检测机制，自动获取存在困难。

## API 请求说明

### 第一题 API

**Page 1-4**:
- **URL**: `https://match.yuanrenxue.cn/api/question/1?page={页码}&m={m参数}`
- **Headers**: User-Agent 标准浏览器 UA, Cookie sessionid

**Page 5**:
- **URL**: 同上
- **Headers**: User-Agent `yuanrenxue`, Cookie sessionid

### 第二题 API

- **URL**: `https://match.yuanrenxue.cn/api/question/2?page={页码}&pageSize=10&m={m参数}`
- **Headers**: User-Agent 标准浏览器 UA（第5页需 `yuanrenxue`），Cookie sessionid
- **响应**: 返回混淆的 JS 代码，eval 执行后再次请求才能获取数据

## 技术栈

- Python 3
- urllib.request (内置)
- hashlib (内置)
- CDP (Chrome DevTools Protocol)
