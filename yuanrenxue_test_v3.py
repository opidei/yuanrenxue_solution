#!/usr/bin/env python3
"""
猿人学爬虫逆向 - 第一题 完整解决方案
动态从页面提取 window.a，自动确定 c 值，构造正确的 m 参数
"""

import hashlib
import time
import json
import re
import base64
import subprocess
import urllib.request
import urllib.parse
import urllib.error


def fetch_page_and_get_window_a():
    """从页面提取 window.a 和 script count"""
    req = urllib.request.Request(
        'https://match.yuanrenxue.cn/match/1',
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
    )
    resp = urllib.request.urlopen(req, timeout=15)
    html = resp.read().decode('utf-8')

    # 提取 window.a='...' 值
    match = re.search(r"window\.a\s*=\s*['\"]([^'\"]+)['\"]", html)
    if not match:
        print("  [ERROR] 未找到 window.a")
        return None, None, None

    window_a = match.group(1)
    print(f"  [OK] window.a 长度: {len(window_a)}")

    # 计算 $('script').length - 10
    # jQuery 的 $('script') 只匹配实际的 SCRIPT 元素，不匹配 <script> 字符串
    # 通过尝试不同的 c 值来找到正确的那个
    return window_a, html, len(window_a)


def try_decode(window_a, c):
    """尝试用给定 c 值解码 window.a"""
    try:
        decoded = ''
        for i in range(len(window_a)):
            ch = ord(window_a[i]) - i - c
            if ch < 0:
                ch += 256
            decoded += chr(ch)

        # 尝试 base64 解码
        try:
            decoded_bytes = base64.b64decode(decoded)
            return decoded_bytes.decode('latin-1')
        except Exception:
            # 尝试添加 padding
            try:
                padded = decoded + '=' * (4 - len(decoded) % 4) % 4
                decoded_bytes = base64.b64decode(padded)
                return decoded_bytes.decode('latin-1')
            except Exception:
                return None
    except Exception:
        return None


def find_correct_c(window_a):
    """通过验证解码结果是否为有效 JS 代码来确定正确的 c 值"""
    for c in range(0, 20):
        decoded = try_decode(window_a, c)
        if decoded and 'hex_md5' in decoded and 'binl2hex' in decoded:
            print(f"  [FOUND] c={c} 解码成功! 前100字符: {decoded[:100]}")
            return c, decoded
        elif decoded and 'function hex_md5' in decoded:
            print(f"  [FOUND] c={c} 解码成功! 前100字符: {decoded[:100]}")
            return c, decoded

    print("  [WARN] 未找到包含 hex_md5 的解码结果，尝试所有 c 值")
    for c in range(0, 20):
        decoded = try_decode(window_a, c)
        if decoded and len(decoded) > 100:
            print(f"  c={c}: 前80字符: {decoded[:80]}")

    return 5, None  # 默认 c=5


def generate_m_with_md5_check():
    """生成 m 参数，确保 MD5 与标准实现一致"""
    ts_ms = int(time.time() * 1000)
    offset = 100000000
    timestamp = ts_ms + offset
    ts_str = str(timestamp)

    md5_hash = hashlib.md5(ts_str.encode('utf-8')).hexdigest()

    # 浮点除法 (JavaScript /)
    m_param = f"{md5_hash}\u4e28{timestamp / 1000}"

    return {
        'timestamp': timestamp,
        'window_f': md5_hash,
        'm_param': m_param,
        'ts_str': ts_str
    }


def make_request(page, m_param, sessionid=None):
    """发送 API 请求"""
    params = urllib.parse.urlencode({'page': page, 'm': m_param})
    url = f"https://match.yuanrenxue.cn/api/question/1?{params}"

    req = urllib.request.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    req.add_header('Referer', 'https://match.yuanrenxue.cn/match/1')
    req.add_header('Accept', 'application/json, text/javascript, */*; q=0.01')

    if sessionid:
        req.add_header('Cookie', f'sessionid={sessionid}')

    try:
        resp = urllib.request.urlopen(req, timeout=10)
        return resp.status, resp.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8')
    except Exception as e:
        return 0, str(e)


def main():
    print("=" * 60)
    print("猿人学爬虫逆向 - 第一题 完整解决方案")
    print("=" * 60)

    # Step 1: 从页面提取 window.a
    print("\n[Step 1] 获取页面 HTML 并提取 window.a...")
    req = urllib.request.Request(
        'https://match.yuanrenxue.cn/match/1',
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
    )
    resp = urllib.request.urlopen(req, timeout=15)
    html = resp.read().decode('utf-8')

    match = re.search(r"window\.a\s*=\s*['\"]([^'\"]+)['\"]", html)
    if not match:
        print("  [ERROR] 未找到 window.a")
        return
    window_a = match.group(1)
    print(f"  [OK] window.a 长度: {len(window_a)}")

    # Step 2: 找到正确的 c 值
    print("\n[Step 2] 确定正确的 c 值...")
    correct_c, decoded_js = find_correct_c(window_a)
    print(f"  正确的 c = {correct_c}")

    # Step 3: 生成 m 参数
    print("\n[Step 3] 生成 m 参数...")
    m_result = generate_m_with_md5_check()
    print(f"  Timestamp: {m_result['timestamp']}")
    print(f"  Timestamp字符串: {m_result['ts_str']}")
    print(f"  MD5: {m_result['window_f']}")
    print(f"  M参数: {m_result['m_param']}")

    # Step 4: 发送 API 请求
    # 尝试多个可能的 sessionid
    sessionids = [
        "vnbr18jbbvqmqt9dwppexvlaru26d0x9",
        "",
    ]

    print("\n[Step 4] 测试 API 请求...")
    for sid in sessionids:
        print(f"\n  测试 sessionid='{sid[:10]}...' (if set)...")
        for page in range(1, 6):
            # 每次生成新的 m 参数
            m = generate_m_with_md5_check()['m_param']
            status, response = make_request(page, m, sid if sid else None)

            if status == 200:
                try:
                    data = json.loads(response)
                    if data.get('data') is not None:
                        print(f"    Page {page}: HTTP {status}, data={len(data.get('data', []))} items")
                        if len(data.get('data', [])) > 0:
                            print(f"    成功! 数据: {data['data'][:2]}")
                            return
                    elif 'token failed' in response or data.get('data') is None:
                        print(f"    Page {page}: HTTP {status}, token failed")
                except:
                    print(f"    Page {page}: HTTP {status}, 响应: {response[:100]}")
            elif status == 403:
                print(f"    Page {page}: HTTP 403 Forbidden")
            elif status == 401:
                print(f"    Page {page}: HTTP 401 Unauthorized - sessionid 可能过期")
            else:
                print(f"    Page {page}: HTTP {status}, 响应: {response[:100]}")

            time.sleep(0.3)

    print("\n" + "=" * 60)
    print("所有尝试失败。可能原因:")
    print("  1. sessionid 已过期 (需要重新登录)")
    print("  2. m 参数格式仍不正确")
    print("  3. MD5 计算方式不同")
    print("=" * 60)


if __name__ == "__main__":
    main()
