# 📋 セットアップ手順書
## 統計占い 自動投稿システム 完全構築ガイド

> **所要時間：** 約2〜3時間（初回のみ）  
> **難易度：** ★★☆☆☆（ターミナル操作が少しできればOK）

---

## STEP 0：全体の流れ

```
[1] アカウント開設（手作業）
    ├─ Anthropic（Claude API）
    ├─ GitHub
    ├─ X Developer
    └─ Threads / Meta Developer

[2] ローカル動作確認（ターミナル）
    └─ 運勢生成スクリプトをPCで動かして確認

[3] GitHubにアップロード（手作業）
    └─ ファイルをGitHubに置く

[4] GitHub Actionsで自動化（設定）
    └─ シークレット（APIキー）を登録する

[5] Webサイトを公開（GitHub Pages）
    └─ URLが発行される
```

---

## STEP 1：Anthropic APIキーを取得する（手作業）

**→ https://console.anthropic.com**

1. 「Sign Up」でアカウント作成（Google認証でOK）
2. ログイン後、左メニュー「API Keys」をクリック
3. 「Create Key」→ キー名を適当に入力（例：`fortune-bot`）
4. 表示されたキーをメモ帳にコピーして保存
   ```
   例: sk-ant-api03-XXXXXXXXXXXXXXXXXXXXXXXX
   ```
   ⚠️ このキーは1度しか表示されません。必ず保存してください。

5. 「Billing」から $5 分のクレジットをチャージ（月150円以下しか使わない）

---

## STEP 2：GitHubアカウントを作成する（手作業）

**→ https://github.com**

1. 「Sign Up」でアカウント作成
2. リポジトリ（プロジェクト保存場所）を新規作成
   - 右上「+」→「New repository」
   - Repository name：`fortune-bot`（何でもOK）
   - **Public**（GitHub Pagesを無料で使うため）を選択
   - 「Create repository」をクリック
3. リポジトリのURLをメモ：
   ```
   https://github.com/あなたのユーザー名/fortune-bot
   ```

---

## STEP 3：X (Twitter) APIキーを取得する（手作業）

**→ https://developer.x.com**

1. 「Sign up for Free Account」でDeveloper登録
   - **Use case:** `Automated Bot`を選択
   - 説明欄：「自動運勢投稿ボット」と入力（英語でもOK）
2. 承認後、「Projects & Apps」→「Default Project」→アプリを選択
3. 「Keys and Tokens」タブを開く
4. 以下の4つをメモ帳に保存：
   ```
   API Key（Consumer Key）    : XXXXXXXXXXXXXXXXXX
   API Secret                : XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
   Access Token               : XXXXXXXXXX-XXXXXXXXXXXXXXXXXXXXXXXXXX
   Access Token Secret        : XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
   ```
5. 「App Settings」→「User authentication settings」→「Edit」
   - App permissions：**Read and Write** に変更（重要！）

---

## STEP 4：Threads APIキーを取得する（手作業）

**→ https://developers.facebook.com**

1. Metaアカウント（Facebookと同じ）でログイン
2. 「My Apps」→「Create App」
3. App Type：「Other」→「Consumer」
4. 「Threads API」を製品として追加
5. Threads アカウントを「テストユーザー」として追加
6. 以下をメモ：
   ```
   Threads User ID    : 数字のID（プロフィールページで確認可能）
   Access Token       : Threads Graph APIで発行
   ```

> **難しい場合：** 最初はXだけ設定してThreadsは後回しでOK！
> main.py はThreadsのキーがなければ自動スキップします。

---

## STEP 5：PCにファイルを配置する（ターミナル操作）

**Macの場合：** ターミナルを開く（Spotlight で「ターミナル」検索）  
**Windowsの場合：** PowerShell or コマンドプロンプト

```bash
# ① ダウンロードフォルダに移動
cd ~/Downloads

# ② fortune_project フォルダを確認
ls fortune_project

# ③ Pythonと必要パッケージをインストール確認
python3 --version   # Python 3.8以上ならOK

# ④ 必要パッケージをインストール
cd fortune_project
pip3 install -r requirements.txt
```

---

## STEP 6：ローカルで動作確認する（ターミナル操作）

```bash
# APIキーを一時的に設定（ターミナルを閉じると消える）
export ANTHROPIC_API_KEY="sk-ant-api03-XXXXXXXX"  # ← Step1でメモしたキー

# 運勢生成スクリプトを実行
cd fortune_project/scripts
python3 generate_fortune.py
```

**成功すると：**
```
🔮 2026年XX月XX日 の運勢を生成中...
📊 ランキングツイートを生成中...
   → 150文字
♈ 牡羊座 を生成中...
   → ツイート: 200文字
...
✅ 保存完了: docs/data/fortune_latest.json
✨ 全ての生成が完了しました！
```

`docs/data/fortune_latest.json` ファイルが作成されたら成功！

---

## STEP 7：GitHubにファイルをアップロードする（手作業）

### 方法A：GitHub Desktop（推奨・簡単）

1. **→ https://desktop.github.com** からインストール
2. 「Add Existing Repository」→ fortune_project フォルダを選択
3. 「Publish repository」でGitHubへアップロード
4. **Public** にチェックを入れて「Publish」

### 方法B：ターミナルで操作

```bash
cd fortune_project
git init
git add .
git commit -m "初回コミット"
git branch -M main
git remote add origin https://github.com/あなたのユーザー名/fortune-bot.git
git push -u origin main
```

---

## STEP 8：GitHubにAPIキーを登録する（手作業）

1. GitHubのリポジトリページを開く
2. 「Settings」タブ → 左メニュー「Secrets and variables」→「Actions」
3. 「New repository secret」で以下を1つずつ追加：

| Name（名前） | Secret（値） |
|------------|------------|
| `ANTHROPIC_API_KEY` | Step1でメモしたキー |
| `X_API_KEY` | Step3でメモしたAPI Key |
| `X_API_SECRET` | Step3でメモしたAPI Secret |
| `X_ACCESS_TOKEN` | Step3でメモしたAccess Token |
| `X_ACCESS_TOKEN_SECRET` | Step3でメモしたAccess Token Secret |
| `THREADS_USER_ID` | Step4でメモしたID（任意） |
| `THREADS_ACCESS_TOKEN` | Step4でメモしたToken（任意） |

---

## STEP 9：GitHub Actionsを手動テスト実行する（手作業）

1. GitHubリポジトリの「Actions」タブを開く
2. 左メニュー「毎日の運勢 自動投稿」をクリック
3. 「Run workflow」→「Run workflow」でボタンをクリック
4. 数分後に ✅ 緑のチェックマークが出たら成功！

---

## STEP 10：Webサイトを公開する（GitHub Pages）

1. GitHubリポジトリの「Settings」タブ
2. 左メニュー「Pages」
3. 「Source」→「Deploy from a branch」
4. Branch：`main` / Folder：`/docs` を選択
5. 「Save」

数分後に以下のURLでサイトが公開される：
```
https://あなたのユーザー名.github.io/fortune-bot/
```

---

## STEP 11：SNSリンクを設定する（手作業）

`docs/index.html` をテキストエディタで開き、以下の箇所を書き換える：

```html
<!-- 変更前 -->
<a href="https://x.com/YOUR_ACCOUNT" ...>

<!-- 変更後（自分のXアカウントに） -->
<a href="https://x.com/あなたのXユーザー名" ...>
```

同様に LINE のリンクと Threads のリンクも書き換えて、再度GitHubにアップロード。

---

## 🚨 よくあるエラーと対処法

| エラー | 原因 | 対処 |
|--------|------|------|
| `ANTHROPIC_API_KEY が設定されていません` | 環境変数未設定 | `export ANTHROPIC_API_KEY="..."` を実行 |
| `ModuleNotFoundError: anthropic` | パッケージ未インストール | `pip3 install -r requirements.txt` を実行 |
| `Twitter API Error 403` | X APIの権限がRead Only | App SettingsでRead and Writeに変更 |
| `FileNotFoundError: fortune_latest.json` | 生成スクリプト未実行 | `python3 generate_fortune.py` を先に実行 |
| GitHub Actions が赤い ❌ | シークレット名のタイポ | Secrets画面でキー名を再確認 |

---

## 💡 運用開始後にやること（週次）

```
毎朝（自動）
  └─ 運勢生成 → X/Threads投稿 → サイト更新

毎週（手作業・15分）
  └─ エンゲージメント確認（いいね数・フォロワー増減）
  └─ 反応の良かった投稿パターンをメモ

毎月（手作業・1時間）
  └─ プロンプトの微調整
  └─ マネタイズ状況確認
  └─ 戦略の見直し（v2戦略ドキュメントを参照）
```

---

## 📞 詰まったときは

このプロジェクトの戦略・コードについては Claude（このチャット）に質問してください。
エラーメッセージをそのままコピペすると解決が速いです。

