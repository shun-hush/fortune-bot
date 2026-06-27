"""
post_to_x.py
────────────────────────────────────────────────
v2戦略準拠の X (Twitter) 投稿スクリプト。

【投稿設計】
1. 親ツイート: ランキング形式（エンゲージメント最大化）
2. リプライ×12: 各星座の詳細（リプライ数を稼ぐ）
3. バズ投稿: 週2〜3回（月・木）
"""

import os
import time
import json
from pathlib import Path
import tweepy

API_KEY             = os.environ.get("X_API_KEY", "")
API_SECRET          = os.environ.get("X_API_SECRET", "")
ACCESS_TOKEN        = os.environ.get("X_ACCESS_TOKEN", "")
ACCESS_TOKEN_SECRET = os.environ.get("X_ACCESS_TOKEN_SECRET", "")
REPLY_INTERVAL_SEC  = 3

def get_client():
    return tweepy.Client(
        consumer_key=API_KEY,
        consumer_secret=API_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET,
        wait_on_rate_limit=True,
    )

def trim(text, limit=280):
    return text[:limit-3] + "..." if len(text) > limit else text

def post_fortune_thread(fortune_data):
    """親ツイート(ランキング) → 12星座リプライ のスレッド投稿"""
    client = get_client()

    print("📤 親ツイートを投稿中...")
    resp = client.create_tweet(text=trim(fortune_data["ranking_tweet"]))
    parent_id = resp.data["id"]
    print(f"   ✅ 親ツイート完了 (ID: {parent_id})")
    time.sleep(REPLY_INTERVAL_SEC)

    signs_order = [
        "牡羊座","牡牛座","双子座","蟹座",
        "獅子座","乙女座","天秤座","蠍座",
        "射手座","山羊座","水瓶座","魚座",
    ]
    for sign in signs_order:
        d = fortune_data["signs"].get(sign)
        if not d:
            continue
        print(f"   {d['emoji']} {sign} をリプライ中...")
        client.create_tweet(
            text=trim(d["tweet"]),
            in_reply_to_tweet_id=parent_id,
        )
        time.sleep(REPLY_INTERVAL_SEC)

    print(f"✨ スレッド完了（親1 + リプライ{len(signs_order)}）")

def post_viral_content(fortune_data):
    """バズ狙いコンテンツを投稿（月・木のみ）"""
    viral = fortune_data.get("viral_post", "").strip()
    if not viral:
        print("⏭ バズコンテンツなし（今日は生成日ではない）")
        return

    client = get_client()
    # 段落ごとに分割、最大3ツイート
    parts = [p.strip() for p in viral.split("\n\n") if p.strip()][:3]

    print("🚀 バズコンテンツを投稿中...")
    prev_id = None
    for i, txt in enumerate(parts):
        if prev_id:
            resp = client.create_tweet(text=trim(txt), in_reply_to_tweet_id=prev_id)
        else:
            resp = client.create_tweet(text=trim(txt))
        prev_id = resp.data["id"]
        print(f"   ✅ ツイート{i+1}/{len(parts)} 完了")
        time.sleep(REPLY_INTERVAL_SEC)

    print("✨ バズコンテンツ投稿完了")

def load_fortune_data():
    json_path = Path(__file__).parent.parent / "docs" / "data" / "fortune_latest.json"
    if not json_path.exists():
        raise FileNotFoundError(f"データファイルが見つかりません: {json_path}")
    with open(json_path, encoding="utf-8") as f:
        return json.load(f)

def main():
    missing = [k for k, v in {
        "X_API_KEY": API_KEY, "X_API_SECRET": API_SECRET,
        "X_ACCESS_TOKEN": ACCESS_TOKEN, "X_ACCESS_TOKEN_SECRET": ACCESS_TOKEN_SECRET,
    }.items() if not v]
    if missing:
        print(f"❌ 環境変数未設定: {', '.join(missing)}")
        exit(1)

    fortune_data = load_fortune_data()
    print(f"📅 {fortune_data['date_jp']} のデータを読み込みました")
    post_fortune_thread(fortune_data)
    time.sleep(10)
    post_viral_content(fortune_data)
    print("\n🎉 X への投稿がすべて完了しました！")

if __name__ == "__main__":
    main()
