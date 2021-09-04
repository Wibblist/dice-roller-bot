import os
from flask import Flask, request
import telebot
from creds import TOKEN, USERNAME, URL
import random
import re

bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)


@bot.message_handler(commands=["start"])
def handle_command(message):
    bot.reply_to(message, "Ya'll ready to roll?")


@bot.message_handler(commands=["help"])
def handle_command(message):
    bot.reply_to(message, "Rolls look like this:\n/1d20+5")


@bot.message_handler(func=lambda message: True, content_types=["text"])
def handle_all_message(message):
    raw = message.text

    if raw[0] == "/":
        roll = raw[1:]

        if roll[:1] == "d":
            roll = roll.replace("d", "1d")
        else:
            roll = roll

        if re.search(r"(\d+d\d+)((\+((\d+d\d+)|\d+))*)?", roll):

            def get_roll(roll):
                inlen = len(roll)
                i = 0

                dnum = ""
                dtype = ""
                dmod = ""

                while roll[i] != "d":
                    dnum += roll[i]
                    i += 1

                i += 1

                if ("+" in roll) or ("-" in roll):
                    while not ((roll[i] == "+") or (roll[i] == "-")):
                        dtype += roll[i]
                        i += 1

                    dmod += roll[i]

                    i += 1

                    while not (i == inlen):
                        dmod += roll[i]
                        i += 1
                else:
                    while not (i == inlen):
                        dtype += roll[i]
                        i += 1

                    dmod = 0

                if dnum == "":
                    dnum = 1
                else:
                    dnum = int(dnum)

                dtype = int(dtype)
                dmod = int(dmod)

                return dnum, dtype, dmod

            roll_in = get_roll(roll)

            def dice_roll(dinput):

                i = 0
                dnum = dinput[0]
                dtype = dinput[1]
                dmod = dinput[2]
                rolled = 0
                rolls = []
                final = 0

                while i < dnum:
                    rolls.append(random.randint(1, dtype))
                    rolled += rolls[i]
                    i += 1

                final = rolled + dmod

                a = "Rolling: "
                a = "".join([a, str(roll), "\n \n", "("])

                i = 0
                while i < (dnum - 1):
                    a = "".join([a, str(rolls[i]), ",", " "])
                    i += 1
                a = "".join([a, str(rolls[i]), ") "])

                if dmod >= 0:
                    a = "".join([a, "+ ", str(dmod), " = ", str(final)])
                else:
                    a = "".join([a, "- ", str(abs(dmod)), " = ", str(final)])

                if final == 69:
                    a = "".join([a, "\n \nNice."])

                bot.reply_to(message, a)

            dice_roll(roll_in)

        else:
            # bot.reply_to(
            #     message, "Invalid Command. Please Try Again."
            # )
            pass


@server.route("/" + TOKEN, methods=["POST"])
def getMessage():
    json_string = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=URL + TOKEN)
    return "!", 200


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
