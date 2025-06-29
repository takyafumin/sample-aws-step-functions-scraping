# Page Capture Lambda（日本語訳）

このLambda関数はウェブページのスクリーンショットを取得し、画像ファイルとして返します。

## 機能概要

`page_capture` Lambda関数は以下を行います：
- 指定されたURLのページをキャプチャ
- 画像を一時ストレージ（/tmp）に保存
- 画像データをbase64形式とファイルパスで返却
- エラーも丁寧に処理

## 入力フォーマット

`url`フィールドを持つイベントを受け取ります：

```json
{
  "url": "https://example.com"
}
```

## 出力フォーマット

### 成功時レスポンス（HTTP 200）
```json
{
  "statusCode": 200,
  "url": "https://example.com",
  "imagePath": "/tmp/screenshot_request-id.png",
  "imageData": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==",
  "body": "{\"url\": \"https://example.com\", \"imagePath\": \"/tmp/screenshot_request-id.png\", \"message\": \"Page screenshot captured successfully\"}"
}
```

### エラー時レスポンス例
- URLがない場合（HTTP 400）
```json
{
  "statusCode": 400,
  "body": "{\"error\": \"URL not found in input\", \"imageData\": null, \"imagePath\": null}"
}
```
- URL形式が不正な場合（HTTP 400）
```json
{
  "statusCode": 400,
  "body": "{\"error\": \"Invalid URL format: invalid-url\", \"imageData\": null, \"imagePath\": null}"
}
```
- 内部エラー（HTTP 500）
```json
{
  "statusCode": 500,
  "body": "{\"error\": \"Internal server error: error details\", \"imageData\": null, \"imagePath\": null}"
}
```

## 使用例

### 基本的な使い方
```python
event = {"url": "https://example.com"}
response = lambda_handler(event, context)
# 戻り値: {"statusCode": 200, "url": "https://example.com", "imagePath": "/tmp/screenshot_xxx.png", ...}
```

### 日本語URL
```python
event = {"url": "https://example.co.jp/パス"}
response = lambda_handler(event, context)
# 戻り値: {"statusCode": 200, "url": "https://example.co.jp/パス", ...}
```

### Step Functions連携例
この関数は、ウェブスクレイピングのStep Functionsワークフローで使用できます：
```json
{
  "Comment": "ページキャプチャ付きスクレイピングワークフロー",
  "StartAt": "ReceiveSearchWord",
  "States": {
    "ReceiveSearchWord": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:region:account:function:search-word-receiver",
      "Next": "CaptureSearchResults"
    },
    "CaptureSearchResults": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:region:account:function:page-capture",
      "Next": "ProcessImages"
    }
  }
}
```

## 実装詳細

### 現状の実装
テスト用のダミー画像生成になっています。本番運用時は以下のようなブラウザ自動化を利用してください：
- Puppeteer（推奨）
- Playwright
- Lambda Layerでブラウザバイナリを同梱

### 本番運用時の要件
- Lambda互換のChrome/Chromiumバイナリ
- Puppeteer/Playwright/pyppeteer
- Lambda Layer
- メモリ512MB以上推奨
- タイムアウト長め推奨

### 実装例（pyppeteer）
```python
import asyncio
from pyppeteer import launch

async def capture_real_screenshot(url):
    browser = await launch({
        'headless': True,
        'args': [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--no-first-run',
            '--no-zygote',
            '--single-process'
        ]
    })
    page = await browser.newPage()
    await page.setViewport({'width': 1280, 'height': 720})
    await page.goto(url, {'waitUntil': 'networkidle2'})
    screenshot_path = f'/tmp/screenshot_{{context.aws_request_id}}.png'
    await page.screenshot({'path': screenshot_path, 'fullPage': True})
    await browser.close()
    return screenshot_path
```

## テスト

ユニットテスト実行：
```bash
python -m unittest tests.test_page_capture -v
```

全テスト実行：
```bash
python -m unittest discover tests -v
```

## エラー処理

- 入力URLなし
- URL形式不正
- 内部処理エラー
- ファイルシステムエラー

すべてのエラーはログに記録され、適切なHTTPステータスとメッセージで返却されます。

## 関連ファイル

- `src/lambda/page_capture.py` - メインのLambda関数
- `tests/test_page_capture.py` - ユニットテスト
- `docs/page_capture.md` - 本ドキュメント