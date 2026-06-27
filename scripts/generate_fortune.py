"""
generate_fortune.py
───────────────────────────────────────────────
毎日の運勢コンテンツをClaude APIで生成し、
docs/data/fortune_YYYY-MM-DD.json と
docs/data/fortune_latest.json に保存する。

GitHub Actions から呼ばれる他、ローカルでも動作する。
"""

import os
import json
from datetime import date, datetime
from pathlib import Path
import anthropic

# ── 設定 ──────────────────────────────────────
API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")  # 環境変数から取得
MODEL   = "claude-sonnet-4-6"
TODAY   = date.today().strftime("%Y年%m月%d日")
DATE_ID = date.today().strftime("%Y-%m-%d")

# 12星座リスト（絵文字つき）
SIGNS = [
    ("牡羊座", "♈"),
    ("牡牛座", "♉"),
    ("双子座", "♊"),
    ("蟹座",   "♋"),
    ("獅子座", "♌"),
    ("乙女座", "♍"),
    ("天秤座", "♎"),
    ("蠍座",   "♏"),
    ("射手座", "♐"),
    ("山羊座", "♑"),
    ("水瓶座", "♒"),
    ("魚座",   "♓"),
]

# ── プロンプト設計 ──────────────────────────────
SYSTEM_PROMPT = """
あなたは「統計占術師」です。
心理学・出生季節効果・バイオリズム理論などの研究データに基づいた
占いコンテンツを作成する専門家です。

【必須ルール】
- 断言せず「〜の傾向があります」「データでは〜」という表現を使う
- ポジティブで行動を促す内容にする
- 科学的な研究や統計への言及を自然に混ぜる
- 読んだ人が「保存したい」「シェアしたい」と思う内容にする
- 絵文字を適度に使い、視認性を上げる
"""

def call_claude(prompt: str) -> str:
    """Claude APIを呼び出してテキストを返す"""
    client = anthropic.Anthropic(api_key=API_KEY)
    message = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text.strip()


def generate_ranking_tweet() -> str:
    """
    親ツイート：仕事運Top3ランキング形式
    → リプライを誘発し、アルゴリズムを有利にする
    """
    prompt = f"""
{TODAY}の12星座【仕事運ランキング】Top3を発表してください。

【フォーマット（厳守）】
---
📊 {TODAY} 仕事運ランキング

🥇 1位 [星座名]
🥈 2位 [星座名]
🥉 3位 [星座名]

↓ 全12星座の詳細はリプライ欄へ✨
あなたの星座は何位？コメントで教えてください👇

#統計占い #今日の運勢 #仕事運
---

※280文字以内に収めてください
"""
    return call_claude(prompt)


def generate_sign_reply(sign: str, emoji: str) -> str:
    """
    各星座のリプライ用ツイート（280文字以内）
    """
    prompt = f"""
{TODAY}の{sign}の運勢を生成してください。

【フォーマット（厳守）】
{emoji} #{sign}

[総合運を一言で／統計的根拠に触れる]

💼 仕事：[具体的アドバイス]
💰 金運：[一言]
❤️ 恋愛：[一言]

🔑 今日のキーワード：「[キーワード]」

※280文字以内に収めてください（ハッシュタグ含む）
"""
    return call_claude(prompt)


def generate_website_reading(sign: str, emoji: str) -> str:
    """
    Webサイト用の詳細鑑定文（500〜700文字）
    """
    prompt = f"""
{TODAY}の{sign}の詳細な運勢鑑定文を作成してください。

【フォーマット】
## {emoji} {sign}の今日の運勢

**総合運：** ★★★★☆ （例：5段階評価）

[リード文：今日の全体的なエネルギーを2〜3文で。統計的根拠に触れる]

### 💼 仕事・キャリア運
[3〜4文。具体的な行動アドバイスを含む]

### 💰 金運・財運
[2〜3文]

### ❤️ 恋愛・対人運
[2〜3文]

### 🌟 今日のラッキーアクション
- [行動1]
- [行動2]
- [行動3]

**今日のキーワード：**「[キーワード]」

500〜700文字でMarkdown形式で書いてください。
"""
    return call_claude(prompt)


def generate_viral_post() -> str:
    """
    週2〜3回投稿するバズ狙いコンテンツ
    """
    import random
    themes = [
        "12星座を「仕事での動き方」で分類すると？（心理学データより）",
        "生まれ月と「貯金できる人」に相関はあるのか？統計データで検証",
        f"{date.today().strftime('%m月')}に運気が上がりやすい星座ランキング（バイオリズム分析）",
        "星座×血液型で分かる「ストレスの溜まりやすさ」ランキング",
        "「直感が冴える」星座Top5──神経科学の研究から読み解く",
    ]
    theme = random.choice(themes)
    prompt = f"""
次のテーマでXのバズ狙い投稿（スレッド形式）を作ってください。

テーマ：{theme}

【フォーマット】
ツイート1（親）: 結論 or ランキング発表（興味を引く冒頭）
ツイート2（リプライ）: 詳細データ・解説
ツイート3（リプライ）: まとめ + 「保存推奨」のCTA

各ツイートは280文字以内。統計・研究への言及を入れてください。
#統計占い のハッシュタグを最後に。
"""
    return call_claude(prompt)


def save_data(data: dict) -> None:
    """JSONファイルとして保存（日付付き + latest）"""
    base = Path(__file__).parent.parent / "docs" / "data"
    base.mkdir(parents=True, exist_ok=True)

    dated_path = base / f"fortune_{DATE_ID}.json"
    latest_path = base / "fortune_latest.json"

    with open(dated_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    with open(latest_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ 保存完了: {dated_path}")
    print(f"✅ 保存完了: {latest_path}")


def main():
    print(f"🔮 {TODAY} の運勢を生成中...")
    print("=" * 50)

    result = {
        "date": DATE_ID,
        "date_jp": TODAY,
        "generated_at": datetime.now().isoformat(),
        "ranking_tweet": "",
        "signs": {},
        "viral_post": "",
    }

    # ① 親ツイート（ランキング）
    print("📊 ランキングツイートを生成中...")
    result["ranking_tweet"] = generate_ranking_tweet()
    print(f"   → {len(result['ranking_tweet'])}文字")

    # ② 12星座のリプライ + サイト用詳細
    for sign, emoji in SIGNS:
        print(f"{emoji} {sign} を生成中...")
        result["signs"][sign] = {
            "emoji": emoji,
            "tweet": generate_sign_reply(sign, emoji),
            "website": generate_website_reading(sign, emoji),
        }
        print(f"   → ツイート: {len(result['signs'][sign]['tweet'])}文字")

    # ③ バズ狙いコンテンツ（週2〜3のみ生成）
    today_weekday = date.today().weekday()  # 0=月, 1=火...
    if today_weekday in [0, 3]:  # 月・木に生成
        print("🚀 バズコンテンツを生成中...")
        result["viral_post"] = generate_viral_post()

    # 保存
    save_data(result)
    print("\n✨ 全ての生成が完了しました！")
    return result


if __name__ == "__main__":
    if not API_KEY:
        print("❌ エラー: ANTHROPIC_API_KEY が設定されていません")
        print("   export ANTHROPIC_API_KEY='your-key-here' を実行してください")
        exit(1)
    main()
