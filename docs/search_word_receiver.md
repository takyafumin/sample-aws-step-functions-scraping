# Search Word Receiver Lambda（日本語訳）

このLambda関数はAWS Step Functionsの入力から検索ワードを受け取り、JSON形式で返します。

## 機能概要

`search_word_receiver` Lambda関数は以下を行います：
- Step Functionsからの入力を受け取る
- イベントから`searchWord`フィールドを抽出
- 検索ワードを標準化JSON形式で返却
- エラーも丁寧に処理

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
  "body": "{\"searchWord\": \"検索ワード\", \"message\": \"Search word received successfully\"}"
}
```

### エラー時レスポンス例
- 検索ワードがない場合（HTTP 400）
```json
{
  "statusCode": 400,
  "body": "{\"error\": \"Search word not found in input\", \"searchWord\": null}"
}
```
- 内部エラー（HTTP 500）
```json
{
  "statusCode": 500,
  "body": "{\"error\": \"Internal server error: error details\", \"searchWord\": null}"
}
```

## 使用例

### 基本的な使い方
```python
event = {"searchWord": "python プログラミング"}
response = lambda_handler(event, context)
# 戻り値: {"statusCode": 200, "searchWord": "python プログラミング", ...}
```

### 日本語検索ワード
```python
event = {"searchWord": "プログラミング 学習"}
response = lambda_handler(event, context)
# 戻り値: {"statusCode": 200, "searchWord": "プログラミング 学習", ...}
```

### Step Functions連携例
この関数はStep Functionsワークフローの最初のステップとして使用できます：
```json
{
  "Comment": "スクレイピングワークフロー",
  "StartAt": "ReceiveSearchWord",
  "States": {
    "ReceiveSearchWord": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:region:account:function:search-word-receiver",
      "Next": "NextStep"
    }
  }
}
```

## テスト

ユニットテスト実行：
```bash
python -m unittest tests.test_search_word_receiver -v
```

手動テスト：
```bash
python manual_test.py
```

## 関連ファイル

- `src/lambda/search_word_receiver.py` - メインのLambda関数
- `tests/test_search_word_receiver.py` - ユニットテスト
- `manual_test.py` - 手動テストスクリプト