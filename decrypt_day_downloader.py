#!/usr/bin/env python3
"""
DecryptDay 文件下载器
获取文件列表并显示下载链接
"""

import webbrowser
import subprocess
import json
from typing import Optional


def get_user_input(prompt: str) -> str:
    """获取用户输入"""
    return input(prompt).strip()


def open_url(url: str) -> None:
    """在浏览器中打开URL"""
    print(f"正在打开浏览器: {url}")
    webbrowser.open(url)


def extract_file_ids(response_data: dict) -> list[dict]:
    """
    从API响应中提取文件ID和存储类型

    返回: [{"id": "xxx", "storage": "drive.google.com"}, ...]
    """
    files = []

    try:
        raw_data = response_data.get("data", "")
        if isinstance(raw_data, str):
            data = json.loads(raw_data)
        else:
            data = raw_data

        if len(data) > 3 and isinstance(data[3], dict):
            files_info = data[3]
            files_index = files_info.get("files")

            if isinstance(files_index, int):
                file_indices = data[files_index] if files_index < len(data) else []
            elif isinstance(files_index, list):
                file_indices = files_index
            else:
                file_indices = []

            for idx in file_indices:
                if isinstance(idx, int) and idx < len(data) and isinstance(data[idx], dict):
                    file_obj = data[idx]

                    # 获取文件ID
                    id_index = file_obj.get("id")
                    if isinstance(id_index, int) and id_index < len(data):
                        actual_id = data[id_index]

                    # 获取存储类型
                    storage_index = file_obj.get("storage_provider")
                    if isinstance(storage_index, int) and storage_index < len(data):
                        storage = data[storage_index]
                    else:
                        storage = "unknown"

                    if isinstance(actual_id, str):
                        files.append({"id": actual_id, "storage": storage})
                        print(f"  找到文件: {actual_id} ({storage})")
    except Exception as e:
        print(f"解析响应数据时出错: {e}")

    return files


def fetch_file_list(app_id: str, cf_clearance: str) -> Optional[dict]:
    """使用 curl 发送 POST 请求获取文件列表"""
    url = f"https://decrypt.day/app/{app_id}?/files"
    form_data = "163,101,97,112,112,73,100,120,25,99,108,57,115,101,52,48,116,55,48,48,53,53,100,111,102,119,49,120,111,54,49,109,119,120,103,118,101,114,115,105,111,110,101,54,46,52,46,48,105,105,115,80,114,101,109,105,101,114,247"

    curl_cmd = [
        "curl", "-X", "POST", url,
        "-H", "Accept: */*",
        "-H", "Accept-Language: zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6,zh-TW;q=0.5",
        "-H", "Cache-Control: no-cache",
        "-H", "Pragma: no-cache",
        "-H", "Origin: https://decrypt.day",
        "-H", f"Referer: https://decrypt.day/app/{app_id}",
        "-H", "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
        "-H", f"Cookie: cf_clearance={cf_clearance}",
        "-F", f"data={form_data}",
    ]

    print(f"正在请求: {url}")

    try:
        result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            print(f"curl 错误: {result.stderr}")
            return None

    except subprocess.TimeoutExpired:
        print("请求超时")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON 解析错误: {e}")
        print(f"响应内容: {result.stdout[:500]}")
        return None
    except Exception as e:
        print(f"请求出错: {e}")
        return None


def main():
    print("=" * 50)
    print("DecryptDay 文件下载器")
    print("=" * 50)

    # Step 1: 获取应用ID
    print("\n[Step 1] 输入应用信息")
    app_id = get_user_input("请输入应用ID（如 id1467190251）: ")

    if not app_id:
        print("错误: 应用ID不能为空")
        return

    page_url = f"https://decrypt.day/app/{app_id}?/files"

    # Step 2: 打开浏览器让用户通过Cloudflare验证
    print("\n[Step 2] Cloudflare 验证")
    print(f"即将打开浏览器访问: {page_url}")
    print("请在浏览器中完成 Cloudflare 验证")

    input("按 Enter 键打开浏览器...")

    open_url(page_url)

    # Step 3: 让用户输入 cf_clearance
    print("\n[Step 3] 获取 cf_clearance")
    print("请在浏览器中按 F12 打开开发者工具")
    print("切换到 Application（应用） > Cookies > decrypt.day")
    print("找到 cf_clearance 并复制其值")

    cf_clearance = get_user_input("\n请粘贴 cf_clearance 值: ")

    if not cf_clearance:
        print("错误: cf_clearance 不能为空")
        return

    # Step 4: 发送请求获取文件列表
    print("\n[Step 4] 获取文件列表")
    response_data = fetch_file_list(app_id, cf_clearance)

    if not response_data:
        print("获取文件列表失败")
        return

    # Step 5: 解析并显示文件列表
    print("\n[Step 5] 解析文件列表")
    files = extract_file_ids(response_data)

    if not files:
        print("未找到可下载的文件")
        return

    # Step 6: 显示下载链接
    print("\n" + "=" * 60)
    print("下载链接列表")
    print("=" * 60)

    referer = f"https://decrypt.day/app/{app_id}"

    for i, file_info in enumerate(files, 1):
        file_id = file_info["id"]
        storage = file_info["storage"]
        download_url = f"https://decrypt.day/app/{app_id}/dl/{file_id}"
        print(f"\n文件 {i}: {file_id}")
        print(f"  存储类型: {storage}")
        print(f"  下载链接: {download_url}")
        print(f"  Referer: {referer}")

    print("\n" + "=" * 60)
    print("请在浏览器中打开下载链接，需要携带 Referer")
    print("=" * 60)


if __name__ == "__main__":
    main()
