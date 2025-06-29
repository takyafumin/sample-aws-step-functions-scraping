# Google Search API Lambda（日本語訳）

このLambda関数はGoogle Custom Search APIを使い、指定した検索ワードの上位5件の検索結果URLを取得します。

## 機能概要

`google_search_api` Lambda関数は以下を行います：
- AWS Step Functionsから検索ワードを受け取る
- Google Custom Search APIを呼び出して検索結果を取得
- 上位5件のURLを抽出
- 標準化されたJSON形式でURLを返す
- API障害や設定不足などのエラーも丁寧に処理

## 設定要件

このLambda関数には以下の環境変数が必要です：
- `GOOGLE_API_KEY`: Custom Search API用のGoogle APIキー
- `GOOGLE_SEARCH_ENGINE_ID`: Google Custom Search Engine ID

### Google Custom Search APIのセットアップ手順
1. [Google Cloud Console](https://console.cloud.google.com/)でCustom Search APIを有効化
2. APIキーを作成
3. [Google CSE](https://cse.google.com/)でカスタム検索エンジンを作成
4. Lambdaの環境変数にAPIキーと検索エンジンIDを設定

## 入力フォーマット

`searchWord`フィールドを持つイベントを受け取ります：

```json
{
  "searchWord": "検索ワード"
}
```

## 出力フォーマット

### 成功時レスポンス（HTTP 200）
```json
{
  "statusCode": 200,
  "searchWord": "検索ワード",
  "urls": [
    "https://example1.com",
    "https://example2.com",
    ...
  ],
  "body": "{\"searchWord\": \"検索ワード\", \"urls\": [...], \"message\": \"Found 5 search results\"}"
}
```

### エラー時レスポンス例
- 検索ワードがない場合（HTTP 400）
- 設定不足（HTTP 500）
- API障害（HTTP 500）

## 使用例

### 基本的な使い方
```python
event = {"searchWord": "python プログラミング"}
response = lambda_handler(event, context)
# 戻り値例: {"statusCode": 200, "searchWord": "python プログラミング", "urls": [...]}
```

### 日本語検索ワード
```python
event = {"searchWord": "プログラミング 学習"}
response = lambda_handler(event, context)
```

### Step Functions連携例
```json
{
  "Comment": "Google検索付きスクレイピングワークフロー",
  "StartAt": "ReceiveSearchWord",
  "States": {
    "ReceiveSearchWord": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:region:account:function:search-word-receiver",
      "Next": "GoogleSearch"
    },
    "GoogleSearch": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:region:account:function:google-search-api",
      "End": true
    }
  }
}
```

## 特徴

- **上位5件返却**
- **エラー処理**: API障害・ネットワーク障害・設定不足もカバー
- **多言語対応**: 日本語などUnicode検索ワードもOK
- **タイムアウト保護**: APIリクエストは30秒タイムアウト
- **ロギング**: 詳細なログ出力
- **Step Functions連携設計**

## テスト

ユニットテスト実行：
```bash
python -m unittest tests.test_google_search_api -v
```

全テスト実行：
```bash
python -m unittest discover tests -v
```

## 関連ファイル

- `src/lambda/google_search_api.py` - メインのLambda関数
- `tests/test_google_search_api.py` - ユニットテスト
- `docs/google_search_api.md` - 本ドキュメント

## API利用制限

- 無料枠: 1日100クエリ
- 有料枠: 1日最大10,000クエリ（課金設定必要）

## セキュリティ考慮事項

- APIキーはAWS Secrets Managerや環境変数で安全に管理
- IAM権限は最小限に
- API利用量を監視し、予期せぬ課金に注意
- ユーザー入力を受け付ける場合はバリデーション推奨