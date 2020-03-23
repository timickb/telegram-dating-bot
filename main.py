import logging
import yaml
import codecs
from database import Database
from handler import Handler
from broadcaster import Broadcaster
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters

def init_bot(config, lang, token):
    global db
    global handler
    global bc

    # Initilizing
    db = Database(config)
    handler = Handler(lang)
    updater = Updater(token['botToken'])
    dp = updater.dispatcher
    bc = Broadcaster(db, updater.bot)

    print('Dating Bot started.')

    # Add message handlers
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(MessageHandler(Filters.all, process))
    dp.add_handler(CallbackQueryHandler(callback))
    dp.add_error_handler(error)

    # Start broadcasting thread
    #bc.start()

    # Start bot
    updater.start_polling()
    updater.idle()


def start(bot, update):
    # Get user Telegram ID
    uid = str(update.message.from_user.id)
    cid = update.message.chat_id
    # Fimd user in our database
    user = db.getUserByID(int(uid))

    # If found, continue
    if(user != None):
        if user['dialog_status'] == 'process':
            bot.sendMessage(cid, handler.getLang()['already_in'])
    # Else register him
    else:
        db.addUser({'id': int(uid), 'chat_id': int(cid), 'dialog_status': 'start', 'liked': [], 'disliked': []})
        bot.sendMessage(update.message.chat_id, handler.getLang()['greeting_new'])
        db.updateUserData(int(uid), 'dialog_status', 'write_name')


def help(bot, update):
    bot.sendMessage(update.message.chat_id, handler.getLang()['help'])


def callback(bot, update):
    pass


def process(bot, update):
    handler.handle(db, bot, update)


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    print('Starting Telegram Dating Bot...')

    global logger

    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    try:
        config = None
        lang = None
        token = None
        with codecs.open('config.yml', 'r', 'utf_8_sig') as stream:
            config = yaml.load(stream, Loader=yaml.SafeLoader)
        with codecs.open('token.yml', 'r', 'utf_8_sig') as stream:
            token = yaml.load(stream, Loader=yaml.SafeLoader)
        langFileName = 'lang/' + config['lang'] + '.yml'
        with codecs.open(langFileName, 'r', 'utf_8_sig') as stream:
            lang = yaml.load(stream, Loader=yaml.SafeLoader)
    except IOError as err:
        print(err) 
        print('An error occured while reading config files')
        exit()

    init_bot(config, lang, token)


if __name__ == "__main__":
    main()
