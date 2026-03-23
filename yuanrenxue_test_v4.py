#!/usr/bin/env python3
"""
深度测试 - 检查为什么只有 page 5 成功
"""

import hashlib
import time
import json
import urllib.request
import urllib.parse
import urllib.error


def generate_m():
    ts_ms = int(time.time() * 1000)
    offset = 100000000
    timestamp = ts_ms + offset
    ts_str = str(timestamp)
    md5_hash = hashlib.md5(ts_str.encode('utf-8')).hexdigest()
    m_param = f"{md5_hash}\u4e28{timestamp / 1000}"
    return m_param, timestamp, ts_str, md5_hash


def make_request(page, m_param, sessionid):
    params = urllib.parse.urlencode({'page': page, 'm': m_param})
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


def main():
    sessionid = "vnbr18jbbvqmqt9dwppexvlaru26d0x9"

    print("测试: 同一 m 参数对所有 page 的响应")
    print("=" * 60)

    m, ts, ts_str, md5 = generate_m()
    print(f"使用同一个 m 参数:")
    print(f"  Timestamp: {ts}")
    print(f"  MD5: {md5}")
    print(f"  M: {m}")
    print()

    for page in range(1, 11):
        status, response = make_request(page, m, sessionid)
        try:
            data = json.loads(response)
            has_data = data.get('data') is not None
            token_failed = 'token failed' in response
            print(f"  Page {page:2d}: HTTP {status}, token_failed={token_failed}, has_data={has_data}, items={len(data.get('data', []))}")
        except:
            print(f"  Page {page:2d}: HTTP {status}, raw: {response[:80]}")

    print()
    print("测试: 每个 page 使用独立的 m 参数")
    print("=" * 60)

    all_results = []
    for page in range(1, 11):
        m_new, ts_new, _, md5_new = generate_m()
        status, response = make_request(page, m_new, sessionid)
        try:
            data = json.loads(response)
            has_data = data.get('data') is not None
            token_failed = 'token failed' in response
            items = data.get('data', [])
            print(f"  Page {page:2d}: HTTP {status}, token_failed={token_failed}, items={len(items)}")
            if has_data and len(items) > 0:
                all_results.extend(items)
        except:
            print(f"  Page {page:2d}: HTTP {status}, raw: {response[:80]}")
        time.sleep(0.2)

    print(f"\n总计获取数据: {len(all_results)} 条")
    if all_results:
        print(f"数据示例: {all_results[:3]}")


if __name__ == "__main__":
    main()
