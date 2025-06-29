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

#### google_drive_uploader
キャプチャ画像を Google Drive にアップロードし、共有URLを取得する Lambda 関数です。

- **機能**: Base64エンコードされた画像データを Google Drive にアップロードし、共有URLを生成
- **入力**: `{"imageData": "base64画像データ", "filename": "ファイル名", "folderId": "フォルダID"}`
- **出力**: 共有URLとファイル情報を含む JSON レスポンス

詳細は [docs/google_drive_uploader.md](docs/google_drive_uploader.md) を参照してください。

## ディレクトリ構成

```
├── src/
│   └── lambda/
│       ├── __init__.py
│       ├── search_word_receiver.py      # 検索ワード受信Lambda
│       └── google_drive_uploader.py     # Google Drive画像アップロードLambda
├── tests/
│   ├── test_search_word_receiver.py     # 検索ワード受信の単体テスト
│   └── test_google_drive_uploader.py    # Google Driveアップロードの単体テスト
├── docs/
│   ├── search_word_receiver.md          # 検索ワード受信Lambda詳細ドキュメント
│   └── google_drive_uploader.md         # Google DriveアップロードLambda詳細ドキュメント
└── manual_test.py                       # 手動テストスクリプト
```

## テスト実行

```bash
# 単体テスト実行
python -m unittest tests.test_search_word_receiver -v
python -m unittest tests.test_google_drive_uploader -v

# 全テスト実行
python -m unittest discover tests -v

# 手動テスト実行
python manual_test.py
```
