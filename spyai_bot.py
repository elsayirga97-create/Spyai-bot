#!/usr/bin/env python3
"""
SPYAI Trading Bot - Powered by Google Gemini
Analyzes XAU/USD chart screenshots using ICT/SMC framework
"""

import logging
import base64
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai
from PIL import Image
import io

# ============================================================
# CONFIG - Replace with your actual keys
# ============================================================
TELEGRAM_TOKEN = "8809819723:AAGyScA3OuYdMlYhi_oMfI5LyLStCp6sfbo"
GEMINI_API_KEY = "AQ.Ab8RN6J3EcMscT_bk-S8m8Bx-xwnP_R4AlpLAG5n4EkMBnFeyA"
# ============================================================

# Setup Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

SPYAI_PROMPT = """You are SPYAI — an elite ICT/SMC trading analyst specializing in XAU/USD (Gold).

Analyze this chart screenshot and provide a complete trading analysis.

RULES:
- ONE direction only (Bullish OR Bearish — no mixed signals)
- Single sniper entry only
- Minimum 1:2 Risk:Reward
- Account: Exness Standard Cent, 2% max risk
- Use ICT/SMC terminology: OB, FVG, BOS, CHoCH, Supply/Demand zones, Kill Zones, Asian Range

OUTPUT FORMAT (use exactly this structure):

━━━━━━━━━━━━━━━━━━━━
⚡ SPYAI ANALYSIS — XAU/USD
━━━━━━━━━━━━━━━━━━━━

📊 BIAS: [BULLISH 🟢 / BEARISH 🔴]

🔍 STRUCTURE:
• HTF Trend: [direction]
• BOS/CHoCH: [details]
• Key Level: [price]

🎯 SETUP:
• Entry Zone: [price range]
• Trigger: [OB/FVG/etc confirmation]
• Dead Zone: [avoid these levels]

📍 TRADE LEVELS:
┌─────────────────────┐
│ 🎯 ENTRY : [price]  │
│ 🛑 SL    : [price]  │
│ ✅ TP1   : [price]  │
│ 🏆 TP2   : [price]  │
└─────────────────────┘

📐 R:R RATIO: 1:[ratio]

💰 LOT SIZING (Cent Account):
• $50 balance → 0.01 lots
• $100 balance → 0.02 lots
• $200 balance → 0.04 lots

🗺️ PRICE MAP:
[ASCII price map showing key levels]

⚠️ INVALIDATION: [what cancels this setup]

━━━━━━━━━━━━━━━━━━━━
🔐 SPYAI | ICT/SMC FRAMEWORK
━━━━━━━━━━━━━━━━━━━━"""


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    welcome = """
⚡ *SPYAI ACTIVATED* ⚡

Welcome fam! I'm your ICT/SMC trading analyst.

📸 *How to use:*
Just send me a chart screenshot and I'll give you:
• Full ICT/SMC analysis
• Sniper entry + SL/TP levels
• Lot sizing for your cent account

🔥 *Supported pairs:* XAU/USD (Gold) primary

Send your chart whenever you're ready! 🎯
    """
    await update.message.reply_text(welcome, parse_mode='Markdown')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = """
📖 *SPYAI HELP*

*Commands:*
/start — Start the bot
/help — Show this message

*How to get analysis:*
1. Take screenshot of your chart (1H, 15M, or 5M)
2. Send the image here
3. Optionally add: timeframe + EAT time
4. Get full SPYAI breakdown instantly!

*Example message with image:*
"15M chart, 09:30 EAT"

⚡ One direction. One entry. No noise.
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def analyze_chart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Analyze chart screenshot with Gemini"""
    
    # Get user caption/message if any
    user_context = ""
    if update.message.caption:
        user_context = f"\nUser context: {update.message.caption}"
    
    # Send loading message
    loading_msg = await update.message.reply_text(
        "⏳ SPYAI analyzing your chart...\nScanning structure, zones & setups 🔍"
    )
    
    try:
        # Get the photo (highest resolution)
        photo = update.message.photo[-1]
        photo_file = await context.bot.get_file(photo.file_id)
        
        # Download image as bytes
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(photo_file.file_path) as response:
                image_bytes = await response.read()
        
        # Open with PIL
        image = Image.open(io.BytesIO(image_bytes))
        
        # Build prompt with user context
        full_prompt = SPYAI_PROMPT
        if user_context:
            full_prompt += f"\n\nAdditional context from trader:{user_context}"
        
        # Send to Gemini
        response = model.generate_content([full_prompt, image])
        analysis = response.text
        
        # Delete loading message
        await loading_msg.delete()
        
        # Send analysis
        await update.message.reply_text(analysis)
        
    except Exception as e:
        await loading_msg.delete()
        error_msg = f"❌ Analysis failed fam!\n\nError: {str(e)}\n\nTry sending the chart again."
        await update.message.reply_text(error_msg)
        logger.error(f"Analysis error: {e}")


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages"""
    await update.message.reply_text(
        "📸 Send me a chart screenshot fam!\n\nI need to see the chart to give you the analysis. 🎯"
    )


def main():
    """Start the bot"""
    print("🚀 SPYAI Bot starting...")
    print("⚡ Powered by Google Gemini")
    print("📊 ICT/SMC Framework loaded")
    print("✅ Ready to analyze charts!\n")
    
    # Build application
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.PHOTO, analyze_chart))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    # Run bot
    print("Bot is running... Press Ctrl+C to stop")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
