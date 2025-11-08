import os
import time
import json
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import requests
from database import DB
from datetime import datetime

load_dotenv()

BOT_TOKEN = os.getenv('8524275835:AAFM43obbCw8_CtGlG8dkW_Cz6LoDkjcj7M')
ADMIN_ID = int(os.getenv('ADMIN_ID', '8321313612'))
DATABASE_PATH = os.getenv('DATABASE_PATH', 'data.db')
PAYMENT_PROVIDER = os.getenv('PAYMENT_PROVIDER', 'idpay')  # or payir
IDPAY_API_KEY = os.getenv('IDPAY_API_KEY')
BASE_URL = os.getenv('BASE_URL', 'https://example.com')

db = DB(DATABASE_PATH)

app = Flask(__name__)

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

def send_message(chat_id, text):
    try:
        requests.post(f"{TELEGRAM_API}/sendMessage", data={"chat_id": chat_id, "text": text})
    except Exception as e:
        print('send_message error', e)

def forward_message(chat_id, from_chat_id, message_id):
    try:
        resp = requests.post(f"{TELEGRAM_API}/forwardMessage", data={"chat_id": chat_id, "from_chat_id": from_chat_id, "message_id": message_id})
        return resp.json()
    except Exception as e:
        print('forward error', e)
        return None

@app.route('/telegram', methods=['POST'])
def telegram_webhook():
    data = request.get_json()
    if not data:
        return jsonify({'ok': False}), 400
    # simple handler: process message text commands
    if 'message' in data:
        msg = data['message']
        text = msg.get('text', '')
        user_id = msg['from']['id']
        username = msg['from'].get('username')
        db.add_user(user_id, username)
        if text == '/start':
            send_message(user_id, 'سلام! برای خرید اشتراک /buy را بزن.')
        elif text == '/buy':
            send_message(user_id, 'برای خرید: /buy_1month or /buy_1week ...')
        elif text.startswith('/buy_'):
            # create payment link
            plan = text.split('/buy_')[-1]
            mapping = {
                '1week': (0,1,0, 30000),
                '1month': (1,0,0, 90000),
                '2months': (2,0,0, 170000),
                '3months': (3,0,0, 250000),
                '4months': (4,0,0, 300000),
            }
            if plan in mapping:
                months, weeks, days, price = mapping[plan]
                # create payment link (IDPay sample)
                order_id = f"{user_id}_{plan}"
                payload = {
                    'order_id': order_id,
                    'amount': price,
                    'name': 'اشتراک ربات',
                    'callback': f"{BASE_URL}/payment/callback"
                }
                headers = {'X-API-KEY': IDPAY_API_KEY, 'Content-Type': 'application/json'}
                try:
                    r = requests.post('https://api.idpay.ir/v1.1/payment', json=payload, headers=headers, timeout=15)
                    d = r.json()
                    link = d.get('link') or d.get('url') or d.get('payment_url')
                    if link:
                        send_message(user_id, f'برای پرداخت این لینک را باز کن:\n{link}')
                    else:
                        send_message(user_id, 'خطا در ساخت لینک پرداخت. لطفا بعدا تلاش کن.')
                except Exception as e:
                    print('payment create error', e)
                    send_message(user_id, 'خطا در ارتباط با درگاه پرداخت.')
        elif text.startswith('/addgroup'):
            parts = text.split()
            if len(parts) >= 3:
                try:
                    tg_id = int(parts[1])
                    title = ' '.join(parts[2:])
                    db.add_group(tg_id, title, user_id)
                    send_message(user_id, 'گروه اضافه شد.')
                except:
                    send_message(user_id, 'آی‌دی گروه باید عددی باشد (-100...)')
            else:
                send_message(user_id, 'مثال: /addgroup -100123456789 نام گروه')
        elif text.startswith('/listgroups'):
            groups = db.list_groups(user_id)
            if not groups:
                send_message(user_id, 'گروهی ثبت نکرده‌اید.')
            else:
                txt = 'گروه‌های شما:\n'
                for g in groups:
                    txt += f"{g['telegram_id']} — {g['title']}\n"
                send_message(user_id, txt)
        elif text.startswith('/createjob'):
            parts = text.split()
            if len(parts) >= 3:
                channel = parts[1]
                try:
                    msg_id = int(parts[2])
                except:
                    send_message(user_id, 'آی‌دی پیام باید عدد باشد.')
                    return jsonify({'ok': True})
                if not db.is_subscribed(user_id):
                    send_message(user_id, 'اشتراک فعال ندارید. لطفا خرید کنید.')
                    return jsonify({'ok': True})
                job_id = db.create_job(user_id, channel, msg_id)
                # forward to user's groups
                groups = db.list_groups(user_id)
                for g in groups:
                    forward_message(g['telegram_id'], channel, msg_id)
                send_message(user_id, f'Job ساخته شد: {job_id}')
            else:
                send_message(user_id, 'مثال: /createjob @channel_username 123')
    return jsonify({'ok': True})

@app.route('/payment/callback', methods=['POST', 'GET'])
def payment_callback():
    # Simple sample for IDPay callback processing
    data = request.get_json() or request.form.to_dict() or request.args.to_dict()
    order_id = data.get('order_id') or data.get('orderId') or data.get('order')
    status = data.get('status') or data.get('success') or data.get('state')
    if order_id:
        try:
            telegram_id = int(order_id.split('_')[0])
        except:
            telegram_id = None
        if telegram_id and status in ('10', '100', 'success', '1', 'OK', 'ok'):
            # Activate example: if plan in order_id decide months
            plan = order_id.split('_')[1] if '_' in order_id else '1month'
            mapping = {
                '1week': (0,1,0),
                '1month': (1,0,0),
                '2months': (2,0,0),
                '3months': (3,0,0),
                '4months': (4,0,0),
            }
            m,w,d = mapping.get(plan, (1,0,0))
            db.set_subscription(telegram_id, months=m, weeks=w, days=d)
            # notify user
            try:
                requests.post(f"{TELEGRAM_API}/sendMessage", data={"chat_id": telegram_id, "text": "✅ پرداخت تایید شد و اشتراک شما فعال شد."})
            except Exception as e:
                print('notify error', e)
    return 'OK', 200

if __name__ == '__main__':
    # For local testing: run Flask dev server
    app.run(host='0.0.0.0', port=10000)
