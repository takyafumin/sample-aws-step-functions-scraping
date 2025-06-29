#!/bin/bash
# Lambda関数のデプロイスクリプト
# 使い方:
#   既存関数の更新: ./deploy_lambda.sh <LAMBDA_FUNCTION_NAME>
#   新規作成:      ./deploy_lambda.sh <LAMBDA_FUNCTION_NAME> [ROLE_ARN HANDLER RUNTIME]
#
# .envファイルにROLE_ARN/HANDLER/RUNTIMEを記載しておけば省略可能

set -e

# .envファイルの読み込み（存在すれば）
if [ -f .env ]; then
  set -a
  source .env
  set +a
fi

if [ -z "$1" ]; then
  echo "Usage: $0 <LAMBDA_FUNCTION_NAME> [ROLE_ARN HANDLER RUNTIME]"
  exit 1
fi

LAMBDA_FUNCTION_NAME=$1
ZIP_FILE=lambda_function.zip
LAMBDA_SRC_DIR=src/lambda
ROLE_ARN=${2:-$ROLE_ARN}
HANDLER=${3:-$HANDLER}
RUNTIME=${4:-$RUNTIME}

# zip化
cd $LAMBDA_SRC_DIR
zip -r ../$ZIP_FILE .
cd ../..

# 関数の存在チェック
echo "Checking if Lambda function '$LAMBDA_FUNCTION_NAME' exists..."
if aws lambda get-function --function-name "$LAMBDA_FUNCTION_NAME" > /dev/null 2>&1; then
  echo "Function exists. Updating code..."
  aws lambda update-function-code --function-name $LAMBDA_FUNCTION_NAME --zip-file fileb://src/$ZIP_FILE
else
  if [ -z "$ROLE_ARN" ] || [ -z "$HANDLER" ] || [ -z "$RUNTIME" ]; then
    echo "新規作成には ROLE_ARN, HANDLER, RUNTIME の指定が必要です。(.env での指定も可)"
    rm src/$ZIP_FILE
    exit 1
  fi
  echo "Function does not exist. Creating new function..."
  aws lambda create-function \
    --function-name $LAMBDA_FUNCTION_NAME \
    --role $ROLE_ARN \
    --handler $HANDLER \
    --runtime $RUNTIME \
    --zip-file fileb://src/$ZIP_FILE
fi

# zipファイル削除
rm src/$ZIP_FILE

echo "Deployed $LAMBDA_FUNCTION_NAME successfully."
