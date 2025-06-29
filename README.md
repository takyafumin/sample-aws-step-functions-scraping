# sample-aws-step-functions-scraping
step functions を使って スクレイピング Lambda を実行する環境を作成する

## 概要

AWS Step Functions を使用してスクレイピング処理を実行するプロジェクトです。

## 構成

### Lambda Functions

#### search_word_receiver
Step Functions の入力から検索ワードを受け取り、次の処理に渡すための Lambda 関数です。

- **機能**: Step Functions イベントから検索ワードを抽出し、JSON 形式で返却
- **入力**: `{"searchWord": "検索ワード"}`
- **出力**: 検索ワードを含む JSON レスポンス

詳細は [docs/search_word_receiver.md](docs/search_word_receiver.md) を参照してください。

#### sheets_url_recorder
Google Drive で取得したファイルの URL を Google Sheets に記録する Lambda 関数です。

- **機能**: URL とメタデータを指定した Google Sheets に記録
- **入力**: `{"url": "ファイルURL", "spreadsheet_id": "シートID"}`
- **出力**: 記録成功・失敗を含む JSON レスポンス

詳細は [docs/sheets_url_recorder.md](docs/sheets_url_recorder.md) を参照してください。

## ディレクトリ構成

```
├── src/
│   └── lambda/
│       ├── __init__.py
│       ├── search_word_receiver.py      # 検索ワード受信Lambda
│       └── sheets_url_recorder.py       # Google SheetsへのURL記録Lambda
├── tests/
│   ├── test_search_word_receiver.py     # search_word_receiver の単体テスト
│   └── test_sheets_url_recorder.py      # sheets_url_recorder の単体テスト
├── docs/
│   ├── search_word_receiver.md          # search_word_receiver の詳細ドキュメント
│   └── sheets_url_recorder.md           # sheets_url_recorder の詳細ドキュメント
├── requirements.txt                     # Python依存関係
└── manual_test.py                       # 手動テストスクリプト
```

## テスト実行

```bash
# 全ての単体テスト実行
python -m unittest discover tests -v

# 個別の単体テスト実行
python -m unittest tests.test_search_word_receiver -v
python -m unittest tests.test_sheets_url_recorder -v

# 手動テスト実行
python manual_test.py
```

## セットアップ

```bash
# 依存関係のインストール
pip install -r requirements.txt
```
