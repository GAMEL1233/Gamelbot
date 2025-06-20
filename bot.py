import requests
import time
import json

TOKEN = "8148850962:AAGaStrNeqjpY9eWiLBco7GFc01f6yjyIsY"
URL = f"https://api.telegram.org/bot{TOKEN}/"

ADMIN_ID = 1416478658

users_file = "users.json"
balance_file = "balances.json"
codes_file = "giftcodes.json"

def load_data(file):
    try:
        with open(file, "r") as f:
            return json.load(f)
    except:
        return {}

def save_data(file, data):
    with open(file, "w") as f:
        json.dump(data, f)

users = load_data(users_file)
balances = load_data(balance_file)
codes = load_data(codes_file)

def send_message(chat_id, text, reply_markup=None):
    data = {"chat_id": chat_id, "text": text}
    if reply_markup:
        data["reply_markup"] = json.dumps(reply_markup)
    requests.post(URL + "sendMessage", data=data)

def get_updates(offset=None):
    params = {"timeout": 100, "offset": offset}
    response = requests.get(URL + "getUpdates", params=params)
    return response.json()["result"]

def main():
    last_update_id = 0
    while True:
        try:
            updates = get_updates(last_update_id + 1)
            for update in updates:
                last_update_id = update["update_id"]
                if "message" in update:
                    handle_message(update["message"])
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(3)

def handle_message(message):
    chat_id = message["chat"]["id"]
    text = message.get("text", "")
    user_id = str(chat_id)

    if user_id not in users:
        users[user_id] = {"ref": None}
        save_data(users_file, users)

    if text == "/start":
        buttons = {
            "keyboard": [
                ["💰 شحن رصيد", "💸 سحب رصيد من البوت"],
                ["🎁 كود هدية", "👥 نظام الإحالات"],
                ["📜 الشروط", "📞 تواصل معنا"],
                ["🛠 لوحة الإدارة"] if chat_id == ADMIN_ID else []
            ],
            "resize_keyboard": True
        }
        send_message(chat_id, "أهلاً بك في بوت جيميليوت، اختر من الأزرار:", buttons)

    elif text == "💰 شحن رصيد":
        send_message(chat_id, "لشحن رصيدك، أرسل حوالة سيريتل كاش إلى الرقم: 94891342 بقيمة لا تقل عن 25000 ل.س ثم أرسل إشعار الحوالة هنا.")

    elif text == "💸 سحب رصيد من البوت":
        send_message(chat_id, "أرسل رقم الهاتف مع المبلغ الذي تريد سحبه ليتم تحويل الرصيد إليك.")

    elif text == "🎁 كود هدية":
        send_message(chat_id, "أرسل الكود الآن:")
        users[user_id]["awaiting_code"] = True
        save_data(users_file, users)

    elif text == "👥 نظام الإحالات":
        ref_link = f"https://t.me/Gaamel_bot?start={user_id}"
        send_message(chat_id, f"رابط الإحالة الخاص بك:\n{ref_link}")

    elif text == "📜 الشروط":
        send_message(chat_id, "📌 الشروط:\n- الحد الأدنى للشحن: 25000 ل.س\n- السحب متاح فقط بعد شحن الرصيد\n- أي تلاعب يؤدي إلى حظر المستخدم")

    elif text == "📞 تواصل معنا":
        send_message(chat_id, "للتواصل مع الدعم: @GAMEL1233")

    elif text == "🛠 لوحة الإدارة" and chat_id == ADMIN_ID:
        send_message(chat_id, "أدخل كلمة مرور لوحة الإدارة:")

    elif text == "gamel2000@" and chat_id == ADMIN_ID:
        buttons = {
            "keyboard": [
                ["📊 عدد المستخدمين", "📢 رسالة جماعية"],
                ["➕ شحن/خصم رصيد", "🎁 توليد كود هدية"],
                ["🗑 حذف جميع الرسائل", "↩ العودة"]
            ],
            "resize_keyboard": True
        }
        send_message(chat_id, "مرحبا بك في لوحة الإدارة 👨‍💼", buttons)

    elif text == "📊 عدد المستخدمين" and chat_id == ADMIN_ID:
        send_message(chat_id, f"عدد المستخدمين: {len(users)}")

    elif users[user_id].get("awaiting_code"):
        code = text.strip()
        if code in codes:
            amount = codes.pop(code)
            balances[user_id] = balances.get(user_id, 0) + amount
            send_message(chat_id, f"✅ تم شحن رصيدك بمقدار {amount} ل.س")
        else:
            send_message(chat_id, "❌ الكود غير صالح أو تم استخدامه.")
        users[user_id]["awaiting_code"] = False
        save_data(users_file, users)
        save_data(balance_file, balances)
        save_data(codes_file, codes)

if __name__ == "__main__":
    main(
