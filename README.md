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

## ディレクトリ構成

```
├── src/
│   └── lambda/
│       ├── __init__.py
│       └── search_word_receiver.py    # 検索ワード受信Lambda
├── tests/
│   └── test_search_word_receiver.py   # 単体テスト
├── docs/
│   └── search_word_receiver.md        # Lambda関数の詳細ドキュメント
├── requirements.txt                   # Python依存関係
├── runtime.txt                        # Pythonバージョン指定
├── Dockerfile                         # Docker環境構築
├── docker-compose.yml                # Docker Compose設定
└── manual_test.py                     # 手動テストスクリプト
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
python -m unittest tests.test_search_word_receiver -v
```

### 方法2: Dockerを使用した実行

#### 1. Dockerイメージのビルド
```bash
docker build -t step-functions-scraping .
```

#### 2. コンテナでテスト実行
```bash
docker run step-functions-scraping
```

### 方法3: Docker Composeを使用した実行

#### 1. テスト実行
```bash
docker compose run app
```

#### 2. Lambda関数のテスト実行
```bash
docker compose run lambda-test
```

## テスト実行

```bash
# 単体テスト実行
python -m unittest tests.test_search_word_receiver -v

# 手動テスト実行
python manual_test.py
```
