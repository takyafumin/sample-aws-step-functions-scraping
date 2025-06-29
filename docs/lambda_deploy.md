# Lambda関数のデプロイ方法（SAM方式）

このプロジェクトのLambdaデプロイはAWS SAM（Serverless Application Model）で一元管理します。

---

## デプロイ手順

### 1. AWS SAM CLIのインストール
公式: https://docs.aws.amazon.com/ja_jp/serverless-application-model/latest/developerguide/install-sam-cli.html

### 2. ビルド
```bash
sam build
```

### 3. デプロイ
```bash
sam deploy --guided
```
- 2回目以降は `sam deploy` だけでOK

### 4. GitHub Actionsからのデプロイ
- Actionsタブ > Deploy SAM Application ワークフローを実行
- AWS認証情報はSecretsに設定

---

## 注意
- Lambdaやリソース定義は `template.yaml` で管理します
- 旧手動デプロイ（deploy_lambda.sh等）は不要です
- `.env` は不要です（SAMテンプレートで一元管理）

---

## 参考
- `template.yaml` を参照
- `.github/workflows/deploy_sam.yml` を参照
