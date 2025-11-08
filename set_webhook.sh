#!/bin/bash
# Usage: ./set_webhook.sh https://yourapp.onrender.com/telegram
if [ -z "$1" ]; then
  echo "Usage: $0 <YOUR_BASE_URL>"
  exit 1
fi
BASE_URL=$1
if [ -z "$BOT_TOKEN" ]; then
  echo "Please export BOT_TOKEN or edit the script to include it."
  exit 1
fi
curl -F "url=${BASE_URL}/telegram" https://api.telegram.org/bot${BOT_TOKEN}/setWebhook
echo
