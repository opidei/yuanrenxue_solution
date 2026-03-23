#!/usr/bin/env python3
"""
猿人学爬虫逆向 - 第一题完整解决方案

核心发现:
1. m 参数格式: {MD5_hash}丨{timestamp/1000}
2. MD5_hash 由混淆的 hex_md5(timestamp) 生成, 与标准 MD5 不同
3. timestamp = Date.now() + 100000000 (毫秒)
4. window.a 经过 XOR(c=5) -> base64 解码 -> JS 代码
5. 服务器使用混淆的 MD5 进行验证

解决方案: 通过浏览器 CDP 获取实时 m 参数, 立即发送 API 请求
"""

import json
import time
import urllib.request
import urllib.parse
import urllib.error


CDP_URL = "http://localhost:3456"


def get_or_create_tab():
    """获取或创建猿人学页面 tab"""
    targets = json.loads(urllib.request.urlopen(f"{CDP_URL}/targets", timeout=5).read())

    # 查找现有 tab
    for t in targets:
        if "match.yuanrenxue.cn/match/1" in t.get("url", ""):
            return t["targetId"]

    # 创建新 tab
    resp = json.loads(urllib.request.urlopen(
        f"{CDP_URL}/new?url=https://match.yuanrenxue.cn/match/1", timeout=15).read())
    target_id = resp["targetId"]
    time.sleep(4)  # 等待页面加载

    # 等待 ready
    for _ in range(15):
        try:
            info = json.loads(urllib.request.urlopen(
                f"{CDP_URL}/info?target={target_id}", timeout=5).read())
            if info.get("ready") == "complete":
                return target_id
        except:
            pass
        time.sleep(0.5)

    return target_id


def get_m_and_session(target_id):
    """从浏览器获取 m 参数和 sessionid"""
    # 获取 window.match1
    try:
        m = urllib.request.urlopen(
            urllib.request.Request(
                f"{CDP_URL}/eval?target={target_id}",
                data=b"window.match1"),
            timeout=5).read().decode().strip()
    except:
        m = None

    # 获取 sessionid
    try:
        cookie = urllib.request.urlopen(
            urllib.request.Request(
                f"{CDP_URL}/eval?target={target_id}",
                data=b"document.cookie.match(/sessionid=([^;]+)/)[1]"),
            timeout=5).read().decode().strip()
    except:
        cookie = None

    return m, cookie


def api_request(page, m, sessionid):
    """发送 API 请求"""
    params = urllib.parse.urlencode({'page': page, 'm': m})
    url = f"https://match.yuanrenxue.cn/api/question/1?{params}"

    req = urllib.request.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    req.add_header('Referer', 'https://match.yuanrenxue.cn/match/1')
    req.add_header('Accept', 'application/json, text/javascript, */*; q=0.01')
    req.add_header('Cookie', f'sessionid={sessionid}')

    try:
        resp = urllib.request.urlopen(req, timeout=10)
        return resp.status, resp.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8')
    except Exception as e:
        return 0, str(e)


def close_tab(target_id):
    """关闭 tab"""
    try:
        urllib.request.urlopen(f"{CDP_URL}/close?target={target_id}", timeout=5)
    except:
        pass


def main():
    print("=" * 60)
    print("猿人学爬虫逆向 - 第一题")
    print("=" * 60)

    target_id = get_or_create_tab()
    print(f"\nTab ID: {target_id}")

    # 获取 m 和 sessionid
    print("\n获取 m 参数...")
    m, sessionid = get_m_and_session(target_id)

    if not m or not sessionid:
        print("  [错误] 无法获取 m 或 sessionid")
        close_tab(target_id)
        return

    print(f"  m = {m}")
    print(f"  sessionid = {sessionid[:10]}...")

    # 获取数据 (pages 1-4)
    print("\n获取数据...")
    all_numbers = []
    for page in range(1, 5):
        status, response = api_request(page, m, sessionid)
        try:
            data = json.loads(response)
            items = data.get('data', [])

            # 检查是否为有效数据 (数字数组)
            if items and all(isinstance(x, int) for x in items):
                print(f"  Page {page}: {items}")
                all_numbers.extend(items)
            elif 'token failed' in response:
                print(f"  Page {page}: token failed (m 已过期)")
                # 刷新页面获取新 m
                if page == 1:
                    print("  刷新页面...")
                    urllib.request.urlopen(
                        f"{CDP_URL}/navigate?target={target_id}&url=https://match.yuanrenxue.cn/match/1",
                        timeout=10)
                    time.sleep(4)
                    m, sessionid = get_m_and_session(target_id)
                    if m:
                        print(f"  新 m = {m}")
                        # 重试当前页
                        status, response = api_request(page, m, sessionid)
                        data = json.loads(response)
                        items = data.get('data', [])
                        if items and all(isinstance(x, int) for x in items):
                            print(f"  Page {page} (重试): {items}")
                            all_numbers.extend(items)
                        else:
                            print(f"  Page {page} (重试): {response[:100]}")
                else:
                    print(f"  Page {page}: {response[:100]}")
            else:
                print(f"  Page {page}: HTTP {status}, {response[:100]}")
        except Exception as e:
            print(f"  Page {page}: 错误 - {e}")

        time.sleep(0.3)

    # 输出结果
    if all_numbers:
        total = sum(all_numbers)
        print(f"\n" + "=" * 40)
        print(f"结果: {len(all_numbers)} 个数字")
        print(f"总和: {total}")
        print("=" * 40)

    close_tab(target_id)


if __name__ == "__main__":
    main()
