import telebot
import json
import jsonpickle
from binance.client import Client
from stock import Stock
import logging
import time

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

#INITIALIZATION
secrets = json.load(open("secrets.json", 'r'))
binance_public_key = secrets['API_KEY']
binance_api_secret = secrets['SECRET_KEY']
TOKEN = secrets['BOT_TOKEN']
chat_id1 = secrets['CHAT_HANDLE1']
chat_id2 = secrets['CHAT_HANDLE2']
bot = telebot.TeleBot(TOKEN)


#MAIN FUNCTIONS
def tks():
    client = Client(binance_public_key, binance_api_secret)
    activity = json.loads(jsonpickle.encode((client.futures_ticker())))
    with open("DATA/futures_test_all.json", "w") as jsonFile:
        c = jsonFile.write(json.dumps(activity, indent=4))
        return

def escapeError(sentence):
    for ch in ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']:
        if ch in sentence:
            sentence = sentence.replace(ch,'\{}'.format(ch))
    return sentence

def completeRsi():
    tks()
    stocks = []
    allData = []
    with open("DATA/futures_test_all.json") as json_file:
        data_DOPE = json.load(json_file)
    for i in data_DOPE:
        stocks.append(i['symbol'])
    try:
        stocks.remove("BTCBUSD")
        stocks.remove('DEFIUSDT')
        stocks.remove('BTCUSDT_210625')
        stocks.remove('ETHUSDT_210625')
        stocks.remove('1000SHIBUSDT')
    except:
        pass
    for ticker in stocks:

        data = []
        stock = Stock(ticker)
        data.append(ticker.upper())
        currentRsi = float("{:.2f}".format(stock.rsi[-1]))
        if currentRsi > 70:
            data.append(str(currentRsi))
        elif currentRsi < 50:
            data.append(str(currentRsi))
        else:
            data.append(currentRsi)
        if stock.highs is None or stock.lows is None:
            continue
        for k, p in zip(stock.lows.tail(2), stock.highs.tail(2)):
            data.append(str(round(100*p/k-100, 2)) + "%")

        data.append('{:,.2f}'.format(float(stock.volume24)))
        data.append("https://www.binance.com/en/futures/{}".format(ticker.upper().split("USDT")[0]+"_USDT"))
        allData.append(data)
    return allData

while True:
    try:
        data_rsi = completeRsi()
        for j in data_rsi:
            msg = str("[%s](%s)\n"%('Binance Futures', escapeError(j[5])) + "*" +j[0] + "*")
            if float(j[1]) > 90:
                if float(j[2].split("%")[0]) > 4.13 or float(j[3].split("%")[0]) > 4.13:
                    bot.send_message(chat_id1, str("[%s](%s)\n"%('Binance Futures', escapeError(j[5])) + "*" +j[0] + "*" + "{}\n".format(escapeError("-> Идет Памп")) + escapeError(j[2]) + " \-\> "+ escapeError(j[3]) + "\nRSI \(15m\): " + escapeError(str(j[1])) + str(" 🔞") + "\n24H Vol: " + escapeError(j[4])+ "USDT") , disable_web_page_preview=True, parse_mode="MarkdownV2")
                    bot.send_message(chat_id2, str("*[%s](%s)*\n"%('Binance Futures', escapeError(j[5])) + "*" +j[0] + "*" + "{}\n".format(escapeError("-> Pump in progress")) + escapeError(j[2]) + " \-\> "+ escapeError(j[3]) +"\nRSI \(15m\): " + escapeError(str(j[1])) + str(" 🔞")) + "\n24H Vol: " + escapeError(j[4]) + "USDT" , disable_web_page_preview=True, parse_mode="MarkdownV2")
                else:
                    bot.send_message(chat_id1, str("[%s](%s)\n"%('Binance Futures', escapeError(j[5])) + "*" +j[0] + "*" + "\-\> Стабильное повышение\n" + escapeError(j[2]) + " \-\> "+ escapeError(j[3]) +"\nRSI \(15m\): " + escapeError(str(j[1])) + str(" 🔞")) + "\n24H Vol: " + escapeError(j[4]) +"USDT" , disable_web_page_preview=True, parse_mode="MarkdownV2")
                    bot.send_message(chat_id2, str("[%s](%s)\n"%('Binance Futures', escapeError(j[5])) + "*" +j[0] + "*" + "\-\> Stable Growth\n" + escapeError(j[2]) + " \-\> "+ escapeError(j[3]) +"\nRSI \(15m\): " + escapeError(str(j[1])) + str(" 🔞")) + "\n24H Vol: " + escapeError(j[4]) , disable_web_page_preview=True, parse_mode="MarkdownV2")
            elif float(j[1]) > 80:
                if float(j[2].split("%")[0]) > 4.13 or float(j[3].split("%")[0]) > 4.13:
                    bot.send_message(chat_id1, str("[%s](%s)\n"%('Binance Futures', escapeError(j[5])) + "*" +j[0] + "*" + "{}\n".format(escapeError("-> Идет Памп")) + escapeError(j[2]) + " \-\> "+ escapeError(j[3]) +"\nRSI \(15m\): " + escapeError(str(j[1])) + str(" ⚠️")) + "\n24H Vol: " + escapeError(j[4])+ "USDT" , disable_web_page_preview=True, parse_mode="MarkdownV2")
                    bot.send_message(chat_id2, str("[%s](%s)\n"%('Binance Futures', escapeError(j[5])) + "*" +j[0] + "*" + "{}\n".format(escapeError("-> Pump in progress")) + escapeError(j[2]) + " \-\> "+ escapeError(j[3]) +"\nRSI \(15m\): " + escapeError(str(j[1])) + str(" ⚠️")) + "\n24H Vol: " + escapeError(j[4])+ "USDT" , disable_web_page_preview=True, parse_mode="MarkdownV2")
                else:
                    bot.send_message(chat_id1, str("[%s](%s)\n"%('Binance Futures', escapeError(j[5])) + "*" +j[0] + "*" + "\-\> Стабильное повышение\n" + escapeError(j[2]) + " \-\> "+ escapeError(j[3]) +"\nRSI \(15m\): " + escapeError(str(j[1])) + str(" ⚠️")) + "\n24H Vol: " + escapeError(j[4])+ "USDT" , disable_web_page_preview=True, parse_mode="MarkdownV2")
                    bot.send_message(chat_id2, str("[%s](%s)\n"%('Binance Futures', escapeError(j[5])) + "*" +j[0] + "*" + "\-\> Stable Growth\n" + escapeError(j[2]) + " \-\> "+ escapeError(j[3]) +"\nRSI \(15m\): " + escapeError(str(j[1])) + str(" ⚠️")) + "\n24H Vol: " + escapeError(j[4])+ "USDT" , disable_web_page_preview=True, parse_mode="MarkdownV2")
            elif float(j[1]) > 76:
                if float(j[2].split("%")[0]) > 4.13 or float(j[3].split("%")[0]) > 4.13:
                    bot.send_message(chat_id1, str("[%s](%s)\n"%('Binance Futures', escapeError(j[5])) + "*" +j[0] + "*" + "{}\n".format(escapeError("-> Идет Памп")) + escapeError(j[2]) + " \-\> "+ escapeError(j[3])+ "\nRSI \(15m\): " + escapeError(str(j[1])) + str(" 🔥")) + "\n24H Vol: " + escapeError(j[4]) + "USDT", disable_web_page_preview=True, parse_mode="MarkdownV2")
                    bot.send_message(chat_id2, str("[%s](%s)\n"%('Binance Futures', escapeError(j[5])) + "*" +j[0] + "*" + "{}\n".format(escapeError("-> Pump in progress")) + escapeError(j[2]) + " \-\> "+ escapeError(j[3]) +"\nRSI \(15m\): " + escapeError(str(j[1])) + str(" 🔥")) + "\n24H Vol: " + escapeError(j[4]) + "USDT", disable_web_page_preview=True, parse_mode="MarkdownV2")
                else:
                    bot.send_message(chat_id1, str("[%s](%s)\n"%('Binance Futures', escapeError(j[5])) + "*" +j[0] + "*" + "\-\> Стабильное повышение\n" + escapeError(j[2]) + " \-\> "+ escapeError(j[3]) +"\nRSI \(15m\): " + escapeError(str(j[1])) + str(" 🔥")) + "\n24H Vol: " + escapeError(j[4]) + "USDT", disable_web_page_preview=True, parse_mode="MarkdownV2")
                    bot.send_message(chat_id2, str("[%s](%s)\n"%('Binance Futures', escapeError(j[5])) + "*" +j[0] + "*" + "\-\> Stable Growth\n" + escapeError(j[2]) + " \-\> "+ escapeError(j[3])+ "\nRSI \(15m\): " + escapeError(str(j[1])) + str(" 🔥")) + "\n24H Vol: " + escapeError(j[4])+ "USDT", disable_web_page_preview=True, parse_mode="MarkdownV2")
            elif float(j[1]) < 27:
                    bot.send_message(chat_id1, str("[%s](%s)\n"%('Binance Futures', escapeError(j[5])) + "*" +j[0] + "*" + "\-\> Стабильное понижение\n" + escapeError(j[2]) + " \-\> "+ escapeError(j[3]) +"\nRSI \(15m\): " + escapeError(str(j[1]))+ str(" 🧊")) + "\n24H Vol: " + escapeError(j[4])+ "USDT" , disable_web_page_preview=True, parse_mode="MarkdownV2")
                    bot.send_message(chat_id2, str("[%s](%s)\n"%('Binance Futures', escapeError(j[5])) + "*" +j[0] + "*" + "\-\> Stable Decrease\n" + escapeError(j[2]) + " \-\> "+ escapeError(j[3]) +"\nRSI \(15m\): " + escapeError(str(j[1])) + str(" 🧊")) + "\n24H Vol: " + escapeError(j[4]) + "USDT", disable_web_page_preview=True, parse_mode="MarkdownV2")
    except Exception as ee:
        logger.error(f"an error: {ee}")
        if ee.startswith("A request to the Telegram API was unsuccessful. Error code: 429."):
            time.sleep(int(ee[-2:]))
    except KeyboardInterrupt:
        logger.info("You pressed CTRL+C")
        exit()
