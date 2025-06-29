# sample-aws-step-functions-scraping
step functions を使って スクレイピング Lambda を実行する環境を作成する

## 概要

AWS Step Functions を使用してスクレイピング処理を実行するプロジェクトです。

## 構成

### Lambda Functions

#### search_word_receiver
Step Functions の入力から検索ワードを受け取り、次の処理に渡すための Lambda 関数です。

- **機能**: Step Functionsイベントから検索ワードを抽出し、JSON形式で返却
- **入力**: `{"searchWord": "検索ワード"}`
- **出力**: 検索ワードを含むJSONレスポンス

詳細は [docs/search_word_receiver.md](docs/search_word_receiver.md) を参照してください。

#### google_search_api
Google Custom Search API を使用して検索結果の上位5件のURLを取得する Lambda 関数です。

- **機能**: Google Custom Search APIを呼び出し、指定された検索ワードで上位5件のURLを取得
- **入力**: `{"searchWord": "検索ワード"}`
- **出力**: 上位5件のURLを含むJSONレスポンス
- **設定**: Google API KeyとSearch Engine IDが環境変数として必要

詳細は [docs/google_search_api.md](docs/google_search_api.md) を参照してください。

#### google_drive_uploader
キャプチャ画像をGoogle Driveにアップロードし、共有URLを取得するLambda関数です。

- **機能**: Base64エンコードされた画像データをGoogle Driveにアップロードし、共有URLを生成
- **入力**: `{"imageData": "base64画像データ", "filename": "ファイル名", "folderId": "フォルダID"}`
- **出力**: 共有URLとファイル情報を含むJSONレスポンス

詳細は [docs/google_drive_uploader.md](docs/google_drive_uploader.md) を参照してください。

#### web_scraper
検索ワードに基づいてウェブスクレイピングを実行するLambda関数です。

- **機能**: 検索ワードを使用してウェブサイトからデータをスクレイピング
- **入力**: 検索ワードを含むJSON
- **出力**: スクレイピングされたデータの配列

#### data_processor
スクレイピングされたデータを処理・クリーニングするLambda関数です。

- **機能**: データのクリーニング、関連性スコア計算、並び替え
- **入力**: スクレイピングされた生データ
- **出力**: 処理済みで関連性スコア付きのデータ

#### results_handler
最終結果をまとめて出力形式を整えるLambda関数です。

- **機能**: 結果の集約、サマリー作成、最終出力フォーマット
- **入力**: 処理済みデータ
- **出力**: 最終結果とサマリー

#### sheets_url_recorder
Google Driveで取得したファイルのURLをGoogle Sheetsに記録するLambda関数です。

- **機能**: URLとメタデータを指定したGoogle Sheetsに記録
- **入力**: `{"url": "ファイルURL", "spreadsheet_id": "シートID"}`
- **出力**: 記録成功・失敗を含むJSONレスポンス

詳細は [docs/sheets_url_recorder.md](docs/sheets_url_recorder.md) を参照してください。

#### page_capture
指定されたURLのページをキャプチャし、画像ファイルとして保存するLambda関数です。

- **機能**: URLのページスクリーンショットを取得し、画像データとして返却
- **入力**: `{"url": "https://example.com"}`
- **出力**: 画像ファイルパスとbase64エンコードされた画像データを含むJSONレスポンス

詳細は [docs/page_capture.md](docs/page_capture.md) を参照してください。

### Step Functions Workflow

すべてのLambda関数はAWS Step Functionsによってオーケストレーションされ、以下のフローで実行されます：

1. 検索ワード受信 → 2. ウェブスクレイピング → 3. データ処理 → 4. 結果ハンドリング

- エラー処理とリトライ機能を含む
- 各ステップ間での適切な入出力連携
- 条件分岐による柔軟な処理フロー

詳細は [docs/step-functions-workflow.md](docs/step-functions-workflow.md) を参照してください。

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
│       ├── search_word_receiver.py      # 検索ワード受信Lambda
│       └── sheets_url_recorder.py       # Google SheetsへのURL記録Lambda
├── tests/
│   ├── test_search_word_receiver.py     # search_word_receiver の単体テスト
│   └── test_sheets_url_recorder.py      # sheets_url_recorder の単体テスト
├── docs/
│   ├── search_word_receiver.md          # search_word_receiver の詳細ドキュメント
│   └── sheets_url_recorder.md           # sheets_url_recorder の詳細ドキュメント
│       └── google_drive_uploader.py     # Google Drive画像アップロードLambda
├── tests/
│   ├── test_search_word_receiver.py     # 検索ワード受信の単体テスト
│   └── test_google_drive_uploader.py    # Google Driveアップロードの単体テスト
├── docs/
│   ├── search_word_receiver.md          # 検索ワード受信Lambda詳細ドキュメント
│   └── google_drive_uploader.md         # Google DriveアップロードLambda詳細ドキュメント
│       ├── search_word_receiver.py    # 検索ワード受信Lambda
│       ├── web_scraper.py             # ウェブスクレイピングLambda
│       ├── data_processor.py          # データ処理Lambda
│       └── results_handler.py         # 結果ハンドリングLambda
├── step-functions/
│   └── scraping-workflow.json         # Step Functions ワークフロー定義
├── tests/
│   ├── test_search_word_receiver.py   # 検索ワード受信Lambda テスト
│   ├── test_web_scraper.py           # ウェブスクレイピングLambda テスト
│   ├── test_data_processor.py        # データ処理Lambda テスト
│   ├── test_results_handler.py       # 結果ハンドリングLambda テスト
│   └── test_workflow_integration.py  # ワークフロー統合テスト
├── tests/
│   ├── test_search_word_receiver.py   # 検索ワード受信Lambda 単体テスト
│   └── test_page_capture.py           # ページキャプチャLambda 単体テスト
├── docs/
│   ├── search_word_receiver.md        # Lambda関数の詳細ドキュメント
│   └── step-functions-workflow.md     # Step Functions ワークフローの詳細
│       └── page_capture.py            # ページキャプチャLambda
├── manual_test.py                     # 手動テストスクリプト
├── requirements.txt                   # Python依存関係
├── runtime.txt                        # Pythonバージョン指定
├── Dockerfile                         # Docker環境構築
└── docker-compose.yml                # Docker Compose設定
```

## 環境セットアップ

このプロジェクトは環境に依存しないPython実行環境を提供します。

### 方法1: ローカル環境での実行

#### 1. Pythonバージョンの確認
```bash
python --version  # Python 3.12推奨
```

#### 2. 依存関係のインストール
```bash
pip install -r requirements.txt
```

#### 3. テスト実行
```bash
python -m unittest discover tests -v
# 個別Lambda関数テスト
python -m unittest tests.test_search_word_receiver -v
python -m unittest tests.test_google_drive_uploader -v
python -m unittest tests.test_web_scraper -v
python -m unittest tests.test_data_processor -v
python -m unittest tests.test_results_handler -v
python -m unittest discover tests -v
# ワークフロー統合テスト
python -m unittest tests.test_workflow_integration -v
```

### 方法2: Dockerを使った実行

#### 1. Dockerイメージのビルド
```bash
docker build -t step-functions-scraping .
```

#### 2. コンテナでテスト実行
```bash
docker run step-functions-scraping
```

### 方法3: Docker Composeを使った実行

#### 1. テスト実行
```bash
docker compose run app
```

#### 2. Lambda関数のテスト実行
```bash
docker compose run lambda-test
```
