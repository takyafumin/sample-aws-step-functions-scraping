# Step Functions ワークフロー定義（日本語訳）

このドキュメントは、スクレイピング自動化システムのAWS Step Functionsワークフローについて説明します。

## ワークフロー概要

このスクレイピングワークフローは、AWS Step Functionsでオーケストレーションされる4つの主要なLambda関数で構成されます：

1. **search_word_receiver** - 検索ワードの受信とバリデーション
2. **web_scraper** - 検索ワードに基づくウェブスクレイピング
3. **data_processor** - スクレイピングデータの処理・クリーニング
4. **results_handler** - 最終結果の整形と出力

## ワークフロー定義

Step Functionsのステートマシン定義は `step-functions/scraping-workflow.json` に記載されています。

### ステート図

```
Start
  ↓
ReceiveSearchWord (search_word_receiver)
  ↓
CheckSearchWordValid (Choice)
  ↓ (有効な場合)
PerformWebScraping (web_scraper)
  ↓
CheckScrapingResults (Choice)
  ↓ (結果あり)
ProcessScrapedData (data_processor)
  ↓
CheckProcessingResults (Choice)
  ↓ (成功時)
HandleFinalResults (results_handler)
  ↓
WorkflowSuccess (Success)
```

### エラー処理

各Lambda関数のステートには：
- 指数バックオフ付きリトライポリシー
- エラーハンドリング用Catchブロック
- ハング防止のタイムアウト
- 条件分岐のChoiceステート

### 入出力連携

各ステート間のデータフロー例：

#### 入力フォーマット
```json
{
  "searchWord": "検索ワード"
}
```

#### ReceiveSearchWord → PerformWebScraping
```json
{
  "statusCode": 200,
  "searchWord": "検索ワード",
  "body": "..."
}
```

#### PerformWebScraping → ProcessScrapedData
```json
{
  "statusCode": 200,
  "searchWord": "検索ワード",
  "scrapedData": [
    {
      "title": "記事タイトル",
      "url": "https://example.com",
      "content": "記事本文...",
      "timestamp": "2024-01-01T10:00:00Z"
    }
  ],
  "itemCount": 2
}
```

#### ProcessScrapedData → HandleFinalResults
```json
{
  "statusCode": 200,
  "searchWord": "検索ワード",
  "processedData": [
    {
      "title": "記事タイトル",
      "url": "https://example.com",
      "content": "クリーン済み記事本文...",
      "relevanceScore": 85.5,
      "wordCount": 150,
      "processedAt": "2024-01-01T10:01:00Z"
    }
  ],
  "itemCount": 2,
  "originalItemCount": 3
}
```

#### 最終出力
```json
{
  "statusCode": 200,
  "finalResults": {
    "searchWord": "検索ワード",
    "processedAt": "2024-01-01T10:02:00Z",
    "summary": {
      "totalItemsFound": 3,
      "totalItemsProcessed": 2,
      "averageRelevanceScore": 78.75,
      "topRelevanceScore": 85.5
    },
    "results": [
      {
        "title": "記事タイトル",
        "url": "https://example.com",
        "content": "クリーン済み記事本文...",
        "relevanceScore": 85.5,
        "wordCount": 150,
        "processedAt": "2024-01-01T10:01:00Z"
      }
    ],
    "metadata": {
      "processingComplete": true,
      "resultsCount": 1,
      "totalResults": 2
    }
  }
}
```

## エラーシナリオ

### 検索ワードなし
最初のChoiceステートでワークフローが失敗します。

### スクレイピング結果なし
スクレイピングで結果が得られなかった場合、`HandleNoResults`ステートに遷移し空の結果セットを返します。

### Lambda関数の失敗
各Lambda関数にはリトライロジックがあります。すべて失敗した場合はエラーハンドリングステートに遷移します。

## デプロイ手順

1. Lambda関数をソースコードから作成
2. `scraping-workflow.json`のARNを更新
3. JSON定義でStep Functionsステートマシンを作成
4. 適切なIAMロール・権限を設定

## テスト

統合テストでワークフロー全体を検証：

```bash
python -m unittest tests.test_workflow_integration -v
```