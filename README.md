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

#### web_scraper
検索ワードに基づいてウェブスクレイピングを実行する Lambda 関数です。

- **機能**: 検索ワードを使用してウェブサイトからデータをスクレイピング
- **入力**: 検索ワードを含む JSON
- **出力**: スクレイピングされたデータの配列

#### data_processor
スクレイピングされたデータを処理・クリーニングする Lambda 関数です。

- **機能**: データのクリーニング、関連性スコア計算、並び替え
- **入力**: スクレイピングされた生データ
- **出力**: 処理済みで関連性スコア付きのデータ

#### results_handler
最終結果をまとめて出力形式を整える Lambda 関数です。

- **機能**: 結果の集約、サマリー作成、最終出力フォーマット
- **入力**: 処理済みデータ
- **出力**: 最終結果とサマリー

### Step Functions Workflow

すべての Lambda 関数は AWS Step Functions によってオーケストレーションされ、以下のフローで実行されます：

1. **検索ワード受信** → 2. **ウェブスクレイピング** → 3. **データ処理** → 4. **結果ハンドリング**

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
└── docs/
    ├── search_word_receiver.md        # Lambda関数の詳細ドキュメント
    └── step-functions-workflow.md     # Step Functions ワークフローの詳細
```

## テスト実行

```bash
# 全テスト実行
python -m unittest discover tests -v

# 個別Lambda関数テスト
python -m unittest tests.test_search_word_receiver -v
python -m unittest tests.test_web_scraper -v
python -m unittest tests.test_data_processor -v
python -m unittest tests.test_results_handler -v

# ワークフロー統合テスト
python -m unittest tests.test_workflow_integration -v
```
