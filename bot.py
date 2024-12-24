import telebot
import requests

# Telegram Bot Token
TELEGRAM_BOT_TOKEN = "8052374051:AAEreHh8QwtLF0jzHiZKgHejHwP3Zj1r2fA"

# DexScreener API URL Template
DEXSCREENER_API = "https://api.dexscreener.io/latest/dex/tokens/{contract_address}"

# Token contract addresses (replace with actual contract addresses)
TOKENS = {
    "Token1": "0x3e43cB385A6925986e7ea0f0dcdAEc06673d4e10",
    "Token2": "0x20ef84969f6d81Ff74AE4591c331858b20AD82CD",
    "Token3": "0x2b0772BEa2757624287ffc7feB92D03aeAE6F12D",
}

# Initialize the bot
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

def format_market_cap(market_cap):
    """
    Format the market cap as 'X.XXM' or 'X.XXB'.
    """
    if market_cap >= 1_000_000_000:
        return f"{market_cap / 1_000_000_000:.2f}B"
    elif market_cap >= 1_000_000:
        return f"{market_cap / 1_000_000:.2f}M"
    else:
        return f"{market_cap:,.0f}"

def get_token_data_with_mc(contract_address):
    """
    Fetch the market cap and price of a token from the DexScreener API.
    """
    url = DEXSCREENER_API.format(contract_address=contract_address)
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if 'pairs' in data and len(data['pairs']) > 0:
            # Extract market cap, price, and name
            token_data = data['pairs'][0]
            name = token_data['baseToken']['name']
            symbol = token_data['baseToken']['symbol']
            market_cap = token_data.get('marketCap', 0)

            # Format market cap
            formatted_market_cap = format_market_cap(market_cap)

            return {"symbol": symbol, "formatted_market_cap": formatted_market_cap, "market_cap": market_cap}
        else:
            return None
    except Exception as e:
        return {"symbol": "Error", "formatted_market_cap": f"Error: {e}", "market_cap": 0}

@bot.message_handler(commands=['price'])
def list_market_caps_sorted(message):
    """
    Telegram command to list the market caps of the tokens sorted by highest market cap.
    """
    token_data_list = []

    for token_name, contract_address in TOKENS.items():
        token_data = get_token_data_with_mc(contract_address)
        if token_data:
            token_data_list.append(token_data)

    # Sort the tokens by market cap in descending order
    sorted_tokens = sorted(token_data_list, key=lambda x: x["market_cap"], reverse=True)

    # Format the response
    response = "📊 Token Data:\n\n"
    for token in sorted_tokens:
        response += f"{token['symbol']}: {token['formatted_market_cap']}\n"

    bot.reply_to(message, response)

# Start the bot
if __name__ == "__main__":
    print("Bot is running. Send /price to get the latest token market caps sorted by highest market cap.")
    bot.polling()
