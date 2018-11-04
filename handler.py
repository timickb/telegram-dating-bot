from telegram import ReplyKeyboardMarkup, KeyboardButton, Bot, Update
from validator import Validator

class Handler:
    def __init__(self, lang):
        self.lang = lang
        self.valr = Validator()
        self.markup = {
            'sexChoice': ReplyKeyboardMarkup([[KeyboardButton(self.lang['man'])], 
                [KeyboardButton(self.lang['woman'])]],
                resize_keyboard=True, one_time_keyboard=True),
            'markChoice': ReplyKeyboardMarkup([[KeyboardButton(self.lang['like'])], [KeyboardButton(self.lang['dislike'])]],
                resize_keyboard=True, one_time_keyboard=True),
            'mainMenu': ReplyKeyboardMarkup([[KeyboardButton(self.lang['menu_continue'])],
                [KeyboardButton(self.lang['menu_stop'])],
                [KeyboardButton(self.lang['menu_delete'])],
                [KeyboardButton(self.lang['menu_edit'])],
                [KeyboardButton(self.lang['menu_show'])]])
        }
    
    def getLang(self):
        return self.lang

    # Print next suitable account which we haven't rate
    def printNext(self, db, bot, update):
        uid = update.message.from_user.id
        cid = update.message.chat_id
        user = db.getUserByID(uid)
        for i in range(len(db.getUsers())):
            if self.valr.checkPartner(user, db.getUsers()[i]):
                partner = db.getUsers()[i]
                db.updateUserData(uid, 'last_profile', partner['id'])
                bot.sendPhoto(cid, partner['photo'], reply_markup=self.markup['markChoice'], 
                    caption=self.lang['account_info'] % (partner['name'], partner['age'], partner['city'], partner['desc']))
                return
        bot.sendMessage(cid, self.lang['no_partners'], reply_markup=None)
    
    def printMe(self, db, bot, update):
        uid = update.message.from_user.id
        cid = update.message.chat_id
        user = db.getUserByID(uid)
        bot.sendPhoto(cid, user['photo'], 
                caption=self.lang['account_info'] % (user['name'], user['age'], user['city'], user['desc']), reply_markup=None)
        

    def handle(self, db, bot, update):
        uid = update.message.from_user.id
        cid = update.message.chat_id
        user = db.getUserByID(uid)
        status = user['dialog_status']

        # Enter username
        if status == 'write_name':
            if self.valr.validName(update.message.text):
                db.updateUserData(uid, 'name', str(update.message.text).strip())
                db.updateUserData(uid, 'dialog_status', 'write_age')
                bot.sendMessage(cid, self.lang['write_age'] % (update.message.text))
            else:
                bot.sendMessage(cid, self.lang['invalid_name'])

        # Enter age
        elif status == 'write_age':
            if self.valr.validAge(update.message.text):
                db.updateUserData(uid, 'age', int(update.message.text))
                db.updateUserData(uid, 'dialog_status', 'write_city')  
                bot.sendMessage(cid, self.lang['write_city'])
            else:
                bot.sendMessage(cid, self.lang['invalid_age'])

        # Enter city
        elif status == 'write_city':
            db.updateUserData(uid, 'city', str(update.message.text))
            db.updateUserData(uid, 'dialog_status', 'write_sex')  
            bot.sendMessage(cid, self.lang['write_sex'], reply_markup=self.markup['sexChoice'])

        # Choose gender
        elif status == 'write_sex':
            if update.message.text == self.lang['man']:
                db.updateUserData(uid, 'sex', 0)
            elif update.message.text == self.lang['woman']:
                db.updateUserData(uid, 'sex', 1)
            else:
                bot.sendMessage(cid, self.lang['incorrect_answer'])
                return
            db.updateUserData(uid, 'dialog_status', 'write_desc')  
            bot.sendMessage(cid, self.lang['write_desc'])

        # Write description
        elif status == 'write_desc':
            db.updateUserData(uid, 'desc', str(update.message.text))
            db.updateUserData(uid, 'dialog_status', 'write_contact')
            bot.sendMessage(cid, self.lang['write_contact'])
        
        # Write contacts
        elif status == 'write_contact':
            db.updateUserData(uid, 'contact', str(update.message.text))
            db.updateUserData(uid, 'dialog_status', 'write_p_sex')
            bot.sendMessage(cid, self.lang['write_p_sex'], reply_markup=self.markup['sexChoice'])

        # Choose partner's gender
        elif status == 'write_p_sex':
            if update.message.text == self.lang['man']:
                db.updateUserData(uid, 'p_sex', 0)
            elif update.message.text == self.lang['woman']:
                db.updateUserData(uid, 'p_sex', 1)
            else:
                bot.sendMessage(cid, self.lang['incorrect_answer'])
                return
            db.updateUserData(uid, 'dialog_status', 'write_p_min_age')  
            bot.sendMessage(cid, self.lang['write_p_min_age'])

        # Enter min partner's age
        elif status == 'write_p_min_age':
            if self.valr.validAge(update.message.text):
                db.updateUserData(uid, 'p_min_age', int(update.message.text))
                db.updateUserData(uid, 'dialog_status', 'write_p_max_age')  
                bot.sendMessage(cid, self.lang['write_p_max_age'])
            else:
                bot.sendMessage(cid, self.lang['invalid_age'])

        # Enter max partner's age
        elif status == 'write_p_max_age':
            if self.valr.validAge(update.message.text):
                db.updateUserData(uid, 'p_max_age', int(update.message.text))
                db.updateUserData(uid, 'dialog_status', 'send_photo')  
                bot.sendMessage(cid, self.lang['send_photo'])
            else:
                bot.sendMessage(cid, self.lang['invalid_age'])

        # Handle the photo and ask if all right
        elif status == 'send_photo':
            photo = update.message.photo[2]
            if self.valr.validPhoto(photo):

                db.updateUserData(uid, 'dialog_status', 'registered')
                db.updateUserData(uid, 'photo', photo.file_id)

                markup = ReplyKeyboardMarkup(
                    [[KeyboardButton(self.lang['confirm_reg'])],
                    [KeyboardButton(self.lang['repeat_reg'])]],
                    resize_keyboard=True, one_time_keyboard=True)

                self.printMe(db, bot, update)
                bot.sendMessage(cid, self.lang['registered'], reply_markup=markup)
            else:
                bot.sendMessage(cid, self.lang['invalid_photo'])
            

        # Start giving accounts
        elif status == 'registered':
            if update.message.text == self.lang['confirm_reg']:
                db.updateUserData(uid, 'dialog_status', 'process')
                db.saveUser(uid)
                self.printNext(db, bot, update)
            elif update.message.text == self.lang['repeat_reg']:
                db.updateUserData(uid, 'dialog_status', 'write_name')
                bot.sendMessage(cid, self.lang['rewrite'])
            else:
                bot.sendMessage(cid, self.lang['incorrect_answer'])

        # Search cycle
        elif status == 'process':
            user = db.getUserByID(uid)
            # Account's rate
            if update.message.text == self.lang['like']:
                mutually = db.addLiked(uid, bot, update)
                if mutually != None:
                    bot.sendMessage(uid, self.lang['mutually'] % (mutually['contact']), reply_markup=None)
                else:
                    self.printNext(db, bot, update)
            elif update.message.text == self.lang['dislike']:
                db.addDisliked(uid, bot, update)
                self.printNext(db, bot, update)
            # Main menu
            elif update.message.text == '1' or update.message.text == self.lang['menu_continue']:
                self.printNext(db, bot, update)
            elif update.message.text == '2' or update.message.text == self.lang['menu_stop']:
                db.updateUserData(uid, 'dialog_status', 'freezed')
                bot.sendMessage(cid, self.lang['profile_freezed'])
            elif update.message.text == '3' or update.message.text == self.lang['menu_delete']:
                db.removeUser(uid)
                bot.sendMessage(cid, self.lang['profile_removed'])
            elif update.message.text == '4' or update.message.text == self.lang['menu_edit']:
                db.updateUserData(uid, 'dialog_status', 'write_name')
                bot.sendMessage(cid, self.lang['rewrite'])
            elif update.message.text == '5' or update.message.text == self.lang['menu_show']:
                self.printMe(db, bot, update)
            else:
                bot.sendMessage(cid, self.lang['incorrect_answer'])

        # Account is freezed
        elif status == 'freezed':
            if update.message.text == '1':
                db.updateUserData(uid, 'dialog_status', 'process')
                self.printNext(db, bot, update)
        # Other situations
        else:
            bot.sendMessage(cid, self.lang['not_understand'])
