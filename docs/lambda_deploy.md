# Lambda関数のデプロイ方法

このプロジェクトのLambda関数は、コマンドラインまたはGitHub Actionsからデプロイできます。

---

## 1. コマンドラインからのデプロイ

### 前提
- AWS CLIがインストールされていること
- `aws configure` で認証情報が設定されていること

### 手順
```sh
chmod +x deploy_lambda.sh
./deploy_lambda.sh <LAMBDA_FUNCTION_NAME>
```

- `<LAMBDA_FUNCTION_NAME>` にはAWS上のLambda関数名を指定してください。

---

## 2. GitHub Actionsからのデプロイ

### 手順
1. リポジトリのSecretsに `AWS_ACCESS_KEY_ID` と `AWS_SECRET_ACCESS_KEY` を登録してください。
2. GitHubのActionsタブから `Deploy Lambda` ワークフローを選択し、Lambda関数名を入力して実行します。

---

## .envファイルによる共通設定

`ROLE_ARN` `HANDLER` `RUNTIME` などの値は `.env` ファイルに記載しておくことで、コマンド実行時に自動で読み込まれます。

例: `.env`
```
ROLE_ARN=arn:aws:iam::123456789012:role/your-lambda-role
HANDLER=main.lambda_handler
RUNTIME=python3.11
```

`.env.example` も参考にしてください。

---

## デプロイ手順

### 1. 既存Lambda関数の更新

```
./deploy_lambda.sh <LAMBDA_FUNCTION_NAME>
```

### 2. Lambda関数の新規作成

- `.env` に必要情報を記載していれば、

```
./deploy_lambda.sh <LAMBDA_FUNCTION_NAME>
```

- もしくは引数で直接指定も可能:

```
./deploy_lambda.sh <LAMBDA_FUNCTION_NAME> <ROLE_ARN> <HANDLER> <RUNTIME>
```

---

## 参考
- `.github/workflows/deploy_lambda.yml` を参照
- `deploy_lambda.sh` を参照
