# Google Drive Uploader Lambda（日本語訳）

このLambda関数は画像をGoogle Driveにアップロードし、アップロードしたファイルの共有URLを返します。

## 機能概要

`google_drive_uploader` Lambda関数は以下を行います：
- AWS Step Functionsからbase64エンコード画像データを受け取る
- Google Drive APIを使って画像をGoogle Driveにアップロード
- ファイルの権限を公開（誰でも閲覧可能）に設定
- アップロードしたファイルの共有URLを返す
- 適切なロギングとともにエラーケースも丁寧に処理

## 入力フォーマット

このLambda関数は以下のフィールドを持つイベントを受け取ります：

```json
{
  "imageData": "base64エンコード画像データ",
  "filename": "任意のファイル名.png",
  "folderId": "任意のGoogle DriveフォルダID"
}
```

### 必須フィールド
- `imageData`: Base64エンコード画像データ（必須）

### 任意フィールド
- `filename`: アップロードするファイル名（デフォルト: "screenshot.png"）
- `folderId`: アップロード先Google DriveフォルダID（デフォルト: ルートフォルダ）

## 出力フォーマット

### 成功時レスポンス（HTTP 200）
```json
{
  "statusCode": 200,
  "shareable_url": "https://drive.google.com/file/d/FILE_ID/view",
  "file_id": "GOOGLE_DRIVE_FILE_ID",
  "filename": "uploaded_filename.png",
  "body": "{\"shareable_url\": \"https://drive.google.com/file/d/FILE_ID/view\", \"file_id\": \"GOOGLE_DRIVE_FILE_ID\", \"filename\": \"uploaded_filename.png\", \"message\": \"Image uploaded to Google Drive successfully\"}"
}
```

### エラー時レスポンス例
- 画像データがない場合（HTTP 400）
```json
{
  "statusCode": 400,
  "body": "{\"error\": \"Image data not found in input\", \"shareable_url\": null}"
}
```
- base64データが不正な場合（HTTP 400）
```json
{
  "statusCode": 400,
  "body": "{\"error\": \"Invalid base64 image data: error details\", \"shareable_url\": null}"
}
```
- アップロード失敗（HTTP 500）
```json
{
  "statusCode": 500,
  "body": "{\"error\": \"Failed to upload to Google Drive: error details\", \"shareable_url\": null}"
}
```
- 内部エラー（HTTP 500）
```json
{
  "statusCode": 500,
  "body": "{\"error\": \"Internal server error: error details\", \"shareable_url\": null}"
}
```

## セットアップ要件

### Google Drive APIのセットアップ
1. Google Cloudプロジェクト作成
2. Google Drive API有効化
3. サービスアカウント作成
4. サービスアカウントの認証情報JSONをダウンロード
5. （特定フォルダを使う場合）そのフォルダをサービスアカウントのメールアドレスと共有

### 環境変数
- `GOOGLE_SERVICE_ACCOUNT_KEY`: サービスアカウント認証情報のJSON文字列

### 依存パッケージ
- `google-api-python-client`
- `google-auth`

## 使用例

### 基本的な画像アップロード
```python
event = {
    "imageData": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==",
    "filename": "screenshot.png"
}
response = lambda_handler(event, context)
# 戻り値例: {"statusCode": 200, "shareable_url": "https://drive.google.com/file/d/FILE_ID/view", ...}
```

### 特定フォルダへのアップロード
```python
event = {
    "imageData": "base64_image_data_here",
    "filename": "captured_image.png",
    "folderId": "1a2b3c4d5e6f7g8h9i0j"
}
response = lambda_handler(event, context)
```

### Step Functions連携例
```json
{
  "Comment": "Google Driveアップロード付きスクレイピングワークフロー",
  "StartAt": "CaptureScreenshot",
  "States": {
    "CaptureScreenshot": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:region:account:function:screenshot-capturer",
      "Next": "UploadToGoogleDrive"
    },
    "UploadToGoogleDrive": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:region:account:function:google-drive-uploader",
      "End": true
    }
  }
}
```

## テスト

ユニットテスト実行：
```bash
python -m unittest tests.test_google_drive_uploader -v
```

## セキュリティ考慮事項

- サービスアカウント認証情報は環境変数などで安全に管理してください
- アップロードファイルはデフォルトで公開設定となるため注意
- 本番運用時はファイルサイズ制限や内容バリデーションも検討してください
- Google Drive APIの利用制限・レート制限に注意

## 関連ファイル

- `src/lambda/google_drive_uploader.py` - メインのLambda関数
- `tests/test_google_drive_uploader.py` - ユニットテスト