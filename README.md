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

#### google_search_api
Google Custom Search API を使用して検索結果の上位5件のURLを取得する Lambda 関数です。

- **機能**: Google Custom Search API を呼び出し、指定された検索ワードで上位5件のURLを取得
- **入力**: `{"searchWord": "検索ワード"}`
- **出力**: 上位5件のURLを含む JSON レスポンス
- **設定**: Google API Key と Search Engine ID が環境変数として必要

詳細は [docs/google_search_api.md](docs/google_search_api.md) を参照してください。

## ディレクトリ構成

```
├── src/
│   └── lambda/
│       ├── __init__.py
│       ├── search_word_receiver.py    # 検索ワード受信Lambda
│       └── google_search_api.py       # Google検索API連携Lambda
├── tests/
│   ├── test_search_word_receiver.py   # search_word_receiver単体テスト
│   └── test_google_search_api.py      # google_search_api単体テスト
├── docs/
│   ├── search_word_receiver.md        # search_word_receiver詳細ドキュメント
│   └── google_search_api.md           # google_search_api詳細ドキュメント
└── manual_test.py                     # 手動テストスクリプト
```

## テスト実行

```bash
# 全ての単体テスト実行
python -m unittest discover tests -v

# search_word_receiver単体テスト実行
python -m unittest tests.test_search_word_receiver -v

# google_search_api単体テスト実行
python -m unittest tests.test_google_search_api -v

# 手動テスト実行
python manual_test.py
```
