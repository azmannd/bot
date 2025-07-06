# -*- coding: utf-8 -*-

import logging
import discord
import google.generativeai as genai

# --- پیکربندی‌ها ---
# در این بخش باید اطلاعات محرمانه خود را وارد کنید.
# هشدار: این اطلاعات را با کسی به اشتراک نگذارید.

# 1. توکن ربات دیسکورد خود را اینجا قرار دهید
# این توکن را از بخش "Bot" در پورتال توسعه‌دهندگان دیسکورد دریافت کنید.
DISCORD_BOT_TOKEN = "161a50061eef65339bcc0311524ffce27849f2c50c89611ba92d216cde5919b6"

# 2. کلید API خود برای Gemini را اینجا قرار دهید
# این کلید را می‌توانید به صورت رایگان از Google AI Studio دریافت کنید.
GEMINI_API_KEY = "AIzaSyARLbIN33FrsjOBSL16duYsfZz4-DE1qLg"

# پیکربندی لاگین برای نمایش اطلاعات در ترمینال
logging.basicConfig(level=logging.INFO)

# پیکربندی مدل هوش مصنوعی Gemini
try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    logging.info("مدل Gemini با موفقیت پیکربندی شد.")
except Exception as e:
    logging.error(f"خطا در پیکربندی Gemini: {e}")
    model = None

# --- منطق اصلی ربات دیسکورد ---

# برای اینکه ربات بتواند محتوای پیام‌ها را بخواند، باید Intents را فعال کنیم.
intents = discord.Intents.default()
intents.message_content = True

# ساخت یک نمونه از کلاینت ربات با Intents مشخص شده
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    """
    این تابع زمانی اجرا می‌شود که ربات با موفقیت به دیسکورد متصل شود.
    یک پیام در ترمینال چاپ می‌کند تا از آنلاین بودن ربات مطمئن شویم.
    """
    print(f'ربات با نام کاربری {client.user} با موفقیت آنلاین شد!')
    print('------')

@client.event
async def on_message(message):
    """
    این تابع به ازای هر پیامی که در سرور ارسال شود، یک بار اجرا می‌شود.
    """
    # 1. اگر پیام ارسال شده توسط خود ربات باشد، آن را نادیده می‌گیریم.
    if message.author == client.user:
        return

    # 2. بررسی می‌کنیم که آیا ربات در پیام منشن (mention) شده است یا خیر.
    # ربات فقط به پیام‌هایی پاسخ می‌دهد که در آن @نام_ربات ذکر شده باشد.
    if client.user.mentioned_in(message):
        
        # 3. بررسی می‌کنیم که آیا مدل هوش مصنوعی آماده به کار است.
        if not model:
            await message.channel.send("متاسفانه در حال حاضر به سرویس هوش مصنوعی متصل نیستم. لطفاً بعداً تلاش کنید.")
            return

        # 4. متن پیام کاربر را تمیز می‌کنیم (نام ربات را از آن حذف می‌کنیم).
        user_message = message.content.replace(f'<@!{client.user.id}>', '').strip()
        user_message = user_message.replace(f'<@{client.user.id}>', '').strip()

        if not user_message:
            await message.channel.send("سلام! چطور میتونم کمکت کنم؟ لطفاً سوالت رو بعد از منشن کردن من بنویس.")
            return

        try:
            # 5. یک پیام "در حال پردازش" برای کاربر ارسال می‌کنیم.
            async with message.channel.typing():
                # 6. پیام کاربر را به مدل Gemini ارسال کرده و منتظر پاسخ می‌مانیم.
                response = model.generate_content(user_message)

                # 7. پاسخ دریافت شده را در کانال دیسکورد ارسال می‌کنیم.
                # اگر پاسخ طولانی بود، آن را به چند بخش تقسیم می‌کنیم.
                if len(response.text) > 2000:
                    for chunk in [response.text[i:i + 2000] for i in range(0, len(response.text), 2000)]:
                        await message.channel.send(chunk)
                else:
                    await message.channel.send(response.text)

        except Exception as e:
            # در صورت بروز خطا، آن را در لاگ ثبت کرده و به کاربر اطلاع می‌دهیم.
            logging.error(f"خطا در دریافت پاسخ از Gemini: {e}")
            await message.channel.send("اوه! یه مشکلی پیش اومد. نتونستم جواب سوالت رو پیدا کنم. 😕")


def main():
    """
    تابع اصلی که ربات را راه‌اندازی و اجرا می‌کند.
    """
    if DISCORD_BOT_TOKEN == "YOUR_DISCORD_BOT_TOKEN" or GEMINI_API_KEY == "YOUR_GEMINI_API_KEY":
        print("!!! هشدار: لطفاً توکن ربات دیسکورد و کلید API Gemini را در کد قرار دهید.")
        return
    
    try:
        print("ربات در حال اجراست...")
        client.run(DISCORD_BOT_TOKEN)
    except discord.errors.LoginFailure:
        print("خطا: توکن ربات دیسکورد نامعتبر است. لطفاً توکن را بررسی کنید.")
    except Exception as e:
        print(f"خطای پیش‌بینی نشده: {e}")

if __name__ == '__main__':
    main()
