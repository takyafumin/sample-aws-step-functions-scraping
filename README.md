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

#### page_capture
指定されたURLのページをキャプチャし、画像ファイルとして保存するLambda関数です。

- **機能**: URLのページスクリーンショットを取得し、画像データとして返却
- **入力**: `{"url": "https://example.com"}`
- **出力**: 画像ファイルパスとbase64エンコードされた画像データを含む JSON レスポンス

詳細は [docs/page_capture.md](docs/page_capture.md) を参照してください。

## ディレクトリ構成

```
├── src/
│   └── lambda/
│       ├── __init__.py
│       ├── search_word_receiver.py    # 検索ワード受信Lambda
│       └── page_capture.py            # ページキャプチャLambda
├── tests/
│   ├── test_search_word_receiver.py   # 検索ワード受信Lambda 単体テスト
│   └── test_page_capture.py           # ページキャプチャLambda 単体テスト
├── docs/
│   ├── search_word_receiver.md        # 検索ワード受信Lambda 詳細ドキュメント
│   └── page_capture.md                # ページキャプチャLambda 詳細ドキュメント
└── manual_test.py                     # 手動テストスクリプト
```

## テスト実行

```bash
# 全ての単体テスト実行
python -m unittest discover tests -v

# 個別のテスト実行
python -m unittest tests.test_search_word_receiver -v
python -m unittest tests.test_page_capture -v

# 手動テスト実行
python manual_test.py
```
