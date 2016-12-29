#!/bin/env python3

import logging
import os
import sys
import time

import telegram

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger('bot')


def handle_updates(bot, update_id):
    for update in bot.getUpdates(offset=update_id, timeout=10):
        logger.info("Message from chatid: " + str(update.message.chat_id))
        update_id = update.update_id + 1

    return update_id

FNAME = "/var/lib/dhcpd/dhcpd.leases"


def send_dhcp_updates(devices, bot, chat_id):
    newdevices = {}
    tmp = {}

    with open(FNAME, 'r') as leases:
        for line in leases:
            if line.startswith("lease "):
                tmp = { "lease": line.split(' ')[1] }
            elif line.startswith("}"):
                newdevices[tmp['hardware']] = tmp
            else:
                try:
                    parts = line.strip().split(' ')
                    tmp[parts[0]] = ' '.join(parts[1:])
                except:
                    pass  # invalid row

        if len(devices.keys()) != 0:
            for mac in newdevices.keys():
                if mac not in devices.keys():
                    logger.info("New mac: " + mac + ", sending a message")
                    text = "New DHCP lease:"
                    for key in newdevices[mac].keys():
                        text += key + " " + newdevices[mac][key] + "\n"
                    bot.sendMessage(chat_id=chat_id, text=text)

        return newdevices



def main():
    if len(sys.argv) > 1:
        api_token = sys.argv[1]
        logger.info("Using API token from command line")
    else:
        if 'tg_api_token' in os.environ.keys():
            api_token = os.environ['tg_api_token']
            logger.info("Using API token from environment variable")
        else:
            logger.error("api token not given on command line and tg_api_token environment variable not present")
            sys.exit(1)

    if len(sys.argv) > 2:
        chat_id = sys.argv[2]
        logger.info("Using chat id from command line")
    else:
        if 'tg_chat_id' in os.environ.keys():
            chat_id = os.environ['tg_chat_id']
            logger.info("Using chat id from environment variable")
        else:
            logger.info("chat id not given on command line and tg_chat_id environment variable not present")
            chat_id = None

    bot = telegram.Bot(api_token)

    try:
        update_id = bot.getUpdates()[0].update_id
    except IndexError:
        update_id = None

    devices = {}

    while True:
        update_id = handle_updates(bot, update_id)
        if chat_id is not None:
            devices = send_dhcp_updates(devices, bot, chat_id)
        time.sleep(5)

if __name__ == "__main__":
    main()
