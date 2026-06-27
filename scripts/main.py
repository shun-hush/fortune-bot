"""
main.py
────────────────────────────────────────────────
全処理のオーケストレーター。
GitHub Actions から呼ばれる。ローカル実行も可能。

実行順:
  1. 運勢コンテンツを生成（Claude API）
  2. docs/data/fortune_latest.json に保存
  3. X (Twitter) に投稿
  4. Threads に投稿
  5. 生成したJSONをGitリポジトリにコミット（Actions内）
"""

import sys
import os

def run():
    print("=" * 60)
    print("🔮 統計占い 自動投稿システム 起動")
    print("=" * 60)

    # Step 1: コンテンツ生成
    print("\n[1/3] 運勢コンテンツを生成中...")
    from generate_fortune import main as generate
    generate()

    # Step 2: X に投稿（環境変数が設定されている場合のみ）
    if os.environ.get("X_API_KEY"):
        print("\n[2/3] X (Twitter) に投稿中...")
        from post_to_x import main as post_x
        post_x()
    else:
        print("\n[2/3] X API キー未設定のためスキップ")

    # Step 3: Threads に投稿（環境変数が設定されている場合のみ）
    if os.environ.get("THREADS_ACCESS_TOKEN"):
        print("\n[3/3] Threads に投稿中...")
        from post_to_threads import main as post_threads
        post_threads()
    else:
        print("\n[3/3] Threads API キー未設定のためスキップ")

    print("\n" + "=" * 60)
    print("✅ 全処理完了！")
    print("=" * 60)

if __name__ == "__main__":
    # スクリプトのあるディレクトリをパスに追加
    sys.path.insert(0, os.path.dirname(__file__))
    run()
