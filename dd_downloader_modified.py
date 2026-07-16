#!/usr/bin/env python3
"""
DecryptDay File Downloader
Retrieve the file list and display the download links
"""


import webbrowser
import subprocess
import json
import requests
from typing import Optional


def get_user_input(prompt: str) -> str:
    """Get User Input"""
    return input(prompt).strip()


def open_url(url: str) -> None:
    """Open the URL in a browser"""
    print(f"Opening the browser: {url}")
    webbrowser.open(url)


def extract_file_ids(response_data: dict) -> list[dict]:
    """
    Extract the file ID and storage type from the API response

    Returns: [{"id": "xxx", "storage": "drive.google.com"}, ...]
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

                    # Get File ID
                    id_index = file_obj.get("id")
                    if isinstance(id_index, int) and id_index < len(data):
                        actual_id = data[id_index]

                    # Get Storage Type
                    storage_index = file_obj.get("storage_provider")
                    if isinstance(storage_index, int) and storage_index < len(data):
                        storage = data[storage_index]
                    else:
                        storage = "unknown"

                    if isinstance(actual_id, str):
                        files.append({"id": actual_id, "storage": storage})
                        print(f"  Find the file: {actual_id} ({storage})")
    except Exception as e:
        print(f"Error occurred while parsing the response data: {e}")

    return files


def fetch_file_list(app_id: str, cf_clearance: str) -> Optional[dict]:
    """Send a POST request to retrieve the file list (preferably using curl; if that fails, use requests)"""
    url = f"https://decrypt.day/app/{app_id}?/files"
    form_data = "YOUR APP'S FORM DATA"

    print(f"Requesting: {url}")

    # Method 1: Using curl
    curl_cmd = [
        "curl", "-X", "POST", url,
        "-H", "Accept: */*",
        "-H", "Accept-Language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "-H", "Cache-Control: no-cache",
        "-H", "Pragma: no-cache",
        "-H", "Origin: https://decrypt.day",
        "-H", f"Referer: https://decrypt.day/app/{app_id}",
        "-H", "User-Agent: YOUR USER AGENT",
        "-H", f"Cookie: cf_clearance={cf_clearance}",
        "-F", f"data={form_data}",
    ]

    try:
        result = subprocess.run(curl_cmd, capture_output=True, text=True, encoding="utf-8", timeout=30)

        if result.returncode == 0 and result.stdout:
            return json.loads(result.stdout)
        else:
            print(f"curl execution failed: {result.stderr}")
    except subprocess.TimeoutExpired:
        print("curl request timed out")
    except FileNotFoundError:
        print("The 'curl' command was not found")
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON response from curl: {e}")
    except Exception as e:
        print(f"Error executing curl: {e}")

    # Method 2: Use requests as a fallback
    print("Trying out an alternative to 'requests'...")

    headers = {
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Origin": "https://decrypt.day",
        "Referer": f"https://decrypt.day/app/{app_id}",
        "User-Agent": "YOUR USER AGENT",
    }

    cookies = {"cf_clearance": cf_clearance}

    files = {"data": (None, form_data)}

    try:
        response = requests.post(url, headers=headers, cookies=cookies, files=files, timeout=30)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Requests Response Status Codes: {response.status_code}")
            return None

    except Exception as e:
        print(f"Requests error: {e}")
        return None


def main():
    print("=" * 50)
    print("DecryptDay File Downloader")
    print("=" * 50)

    # Step 1: Get the App ID
    print("\n[Step 1] Enter App Information")
    app_id = get_user_input("Please enter the app ID (e.g. id1467190251): ")

    if not app_id:
        print("Error: The app ID cannot be empty.")
        return

    page_url = f"https://decrypt.day/app/{app_id}?/files"

    # Step 2: Open a browser and have the user verify their identity through Cloudflare
    print("\n[Step 2] Cloudflare Verification")
    print(f"Your browser will open shortly to visit: {page_url}")
    print("Please complete the Cloudflare verification in your browser")

    input("Press Enter to open the browser...")

    open_url(page_url)

    # Step 3: Have the user enter "cf_clearance"
    print("\n[Step 3] Obtain cf_clearance")
    print("Press F12 in your browser to open the developer tools.")
    print("Go to Application > Cookies > decrypt.day")
    print("Find 'cf_clearance' and copy its value")

    cf_clearance = get_user_input("\nPlease paste the cf_clearance value: ")

    if not cf_clearance:
        print("Error: cf_clearance cannot be null")
        return

    # Step 4: Send a request to retrieve the file list
    print("\n[Step 4] Retrieve the file list")
    response_data = fetch_file_list(app_id, cf_clearance)

    if not response_data:
        print("Failed to retrieve the file list")
        return

    # Step 5: Parse and display the file list
    print("\n[Step 5] Parse the file list")
    files = extract_file_ids(response_data)

    if not files:
        print("No downloadable files were found.")
        return

    # Step 6: Display the download link
    print("\n" + "=" * 60)
    print("List of Download Links")
    print("=" * 60)

    referer = f"https://decrypt.day/app/{app_id}"

    for i, file_info in enumerate(files, 1):
        file_id = file_info["id"]
        storage = file_info["storage"]
        download_url = f"https://decrypt.day/app/{app_id}/dl/{file_id}"
        print(f"\nFile {i}: {file_id}")
        print(f"  Storage Type: {storage}")
        print(f"  Download Link: {download_url}")
        print(f"  Referer: {referer}")

    print("\n" + "=" * 60)
    print("Please open the download link in your browser; the Referer header is required.")
    print("=" * 60)


if __name__ == "__main__":
    main()