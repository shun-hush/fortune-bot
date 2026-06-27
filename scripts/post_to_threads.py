"""
post_to_threads.py
────────────────────────────────────────────────
Meta Threads Graph API を使った自動投稿スクリプト。

事前準備:
  - Meta Developer に Threads API アクセス申請
  - THREADS_USER_ID, THREADS_ACCESS_TOKEN を環境変数に設定
"""

import os
import time
import json
import requests
from pathlib import Path

THREADS_USER_ID    = os.environ.get("THREADS_USER_ID", "")
THREADS_TOKEN      = os.environ.get("THREADS_ACCESS_TOKEN", "")
BASE_URL           = "https://graph.threads.net/v1.0"
INTERVAL_SEC       = 5

def create_container(text: str) -> str:
    """テキストコンテナを作成してIDを返す"""
    url = f"{BASE_URL}/{THREADS_USER_ID}/threads"
    resp = requests.post(url, params={
        "media_type": "TEXT",
        "text": text,
        "access_token": THREADS_TOKEN,
    })
    resp.raise_for_status()
    return resp.json()["id"]

def publish_container(creation_id: str) -> str:
    """コンテナを公開して投稿IDを返す"""
    url = f"{BASE_URL}/{THREADS_USER_ID}/threads_publish"
    resp = requests.post(url, params={
        "creation_id": creation_id,
        "access_token": THREADS_TOKEN,
    })
    resp.raise_for_status()
    return resp.json()["id"]

def post_text(text: str) -> str:
    """テキストを1件投稿して投稿IDを返す"""
    if len(text) > 500:
        text = text[:497] + "..."
    container_id = create_container(text)
    time.sleep(INTERVAL_SEC)
    post_id = publish_container(container_id)
    return post_id

def post_fortune_to_threads(fortune_data: dict) -> None:
    """
    Threads 向け運勢投稿（X と違いスレッド返信 API が限定的）
    → まとめ形式1投稿 + 個別星座投稿を数件に絞る
    """
    print("📤 Threads にランキング投稿中...")
    ranking_text = fortune_data["ranking_tweet"]
    # Threads は 500 文字まで
    post_text(ranking_text[:500])
    print("   ✅ ランキング投稿完了")
    time.sleep(INTERVAL_SEC)

    # 全12星座のまとめ投稿（Threads は長文OKなので凝縮する）
    summary_lines = [f"{fortune_data['date_jp']} 12星座の今日の運勢✨\n"]
    for sign, d in fortune_data["signs"].items():
        # 各星座の1行要約を入れる（ツイートの1行目を使う）
        first_line = d["tweet"].split("\n")[0] if d["tweet"] else ""
        summary_lines.append(f"{d['emoji']} {sign}：{first_line[:40]}")

    summary_lines.append("\n詳細は占いサイトへ👇（プロフィールのリンクから）")
    summary_lines.append("#統計占い #今日の運勢")

    summary_text = "\n".join(summary_lines)
    print("📤 Threads に12星座まとめを投稿中...")
    post_text(summary_text[:500])
    print("   ✅ まとめ投稿完了")

def load_fortune_data() -> dict:
    json_path = Path(__file__).parent.parent / "docs" / "data" / "fortune_latest.json"
    if not json_path.exists():
        raise FileNotFoundError(f"データファイルが見つかりません: {json_path}")
    with open(json_path, encoding="utf-8") as f:
        return json.load(f)

def main():
    if not THREADS_USER_ID or not THREADS_TOKEN:
        print("❌ THREADS_USER_ID / THREADS_ACCESS_TOKEN が未設定です")
        exit(1)

    fortune_data = load_fortune_data()
    print(f"📅 {fortune_data['date_jp']} のデータを読み込みました")
    post_fortune_to_threads(fortune_data)
    print("\n🎉 Threads への投稿がすべて完了しました！")

if __name__ == "__main__":
    main()
