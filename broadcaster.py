from telegram import Bot
import threading

class Broadcaster(threading.Thread):
    def __init__(self, db, bot):
        self.db = db
        self.bot = bot
    
    def run(self):
        print('Broadcasting thread started')

    def broadcast(self, text):
        ids = self.db.getChatIDs()
        for i in range(len(ids)):
            self.bot.sendMessage(ids[i], text)