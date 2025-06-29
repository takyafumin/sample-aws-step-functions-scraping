# Sheets URL Recorder Lambda（日本語訳）

このLambda関数はGoogle DriveファイルのURLをGoogle Sheetsに記録します。

## 機能概要

`sheets_url_recorder` Lambda関数は以下を行います：
- URLとスプレッドシート情報を受け取る
- サービスアカウント認証でGoogle Sheets APIに接続
- タイムスタンプや追加メタデータとともに指定シートにURLを記録
- 適切なHTTPステータスでエラーも丁寧に処理

## 入力フォーマット

以下のフィールドを持つイベントを受け取ります：

```json
{
  "url": "https://drive.google.com/file/d/1234567890/view",
  "spreadsheet_id": "1abcdefghijklmnopqrstuvwxyz1234567890",
  "sheet_range": "Sheet1!A:F",
  "additional_data": {
    "filename": "document.pdf",
    "file_id": "1234567890",
    "file_size": "1024000",
    "description": "Sample document"
  }
}
```

### 必須フィールド
- `url`: 記録するURL（必須）
- `spreadsheet_id`: Google SheetsのスプレッドシートID（必須）

### 任意フィールド
- `sheet_range`: 書き込む範囲（デフォルト: "Sheet1!A:F"）
- `additional_data`: 追加メタデータ

## 出力フォーマット

### 成功時レスポンス（HTTP 200）
```json
{
  "statusCode": 200,
  "url": "https://drive.google.com/file/d/1234567890/view",
  "spreadsheet_id": "1abcdefghijklmnopqrstuvwxyz1234567890",
  "success": true,
  "body": "{\"message\": \"URL recorded successfully\", \"url\": \"...\", \"success\": true}"
}
```

### エラー時レスポンス例
- 必須フィールド不足（HTTP 400）
- サービス利用不可（HTTP 503）
- 内部エラー（HTTP 500）

## シートに記録されるデータ

1. タイムスタンプ（ISO 8601）
2. URL
3. ファイル名（追加データ）
4. ファイルID（追加データ）
5. ファイルサイズ（追加データ）
6. 説明（追加データ）

## 設定

### 環境変数
- `GOOGLE_SHEETS_CREDENTIALS`: サービスアカウント認証情報のJSON文字列

### 必要なGoogle Sheets API権限
- `https://www.googleapis.com/auth/spreadsheets`

## 使用例

### 基本的な使い方
```python
event = {
    "url": "https://drive.google.com/file/d/1234567890/view",
    "spreadsheet_id": "1abcdefghijklmnopqrstuvwxyz1234567890"
}
response = lambda_handler(event, context)
```

### 追加データ付き
```python
event = {
    "url": "https://drive.google.com/file/d/1234567890/view",
    "spreadsheet_id": "1abcdefghijklmnopqrstuvwxyz1234567890",
    "additional_data": {
        "filename": "report.pdf",
        "file_id": "1234567890",
        "file_size": "2048000",
        "description": "Monthly report"
    }
}
response = lambda_handler(event, context)
```

### Step Functions連携例
```json
{
  "Comment": "URL記録ワークフロー",
  "StartAt": "RecordUrlToSheets",
  "States": {
    "RecordUrlToSheets": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:region:account:function:sheets-url-recorder",
      "End": true
    }
  }
}
```

## 依存パッケージ
- `google-api-python-client`
- `google-auth`
- `google-auth-oauthlib`
- `google-auth-httplib2`

## テスト

ユニットテスト実行：
```bash
python -m unittest tests.test_sheets_url_recorder -v
```

全テスト実行：
```bash
python -m unittest discover tests -v
```

## 関連ファイル

- `src/lambda/sheets_url_recorder.py` - メインのLambda関数
- `tests/test_sheets_url_recorder.py` - ユニットテスト
- `requirements.txt` - 依存パッケージ

## セキュリティ考慮事項

- サービスアカウント認証情報はSecrets Managerや環境変数で安全に管理
- API権限は最小限に
- 入力データのバリデーション推奨
- API利用量を監視し、クォータ超過に注意