import json
import os
import logging

class Database:
    def __init__(self, config):
        self.users = []
        self.logger = logging.getLogger(__name__)

        # load user profile from database
        if not os.path.exists("profiles"):
            os.mkdir('profiles')
        files = os.listdir('profiles')
        for i in range(len(files)):
            with open('profiles/'+files[i], 'r', encoding='utf-8') as fh:
                self.users.append(json.load(fh))
    
    def saveUser(self, id):
        for i in range(len(self.users)):
            if self.users[i]['id'] == id:
                with open('profiles/'+str(id)+'.json', 'w', encoding='utf_8') as fh:
                    fh.write(json.dumps(self.users[i], ensure_ascii=False))
        
    
    def addLiked(self, id, bot, update):
        liked_id = self.getUserByID(id)['last_profile']
        for i in range(len(self.users)):
            if(self.users[i]['id'] == id):
                self.users[i]['liked'].append(liked_id)
                # check reciprocity
                partner = None
                for j in range(len(self.users)):
                    if self.users[j]['id'] == liked_id:
                        partner = self.users[j]
                if id in partner['liked']:
                    return partner
                else:
                    return None
    
    def addDisliked(self, id, bot, update):
        disliked_id = self.getUserByID(id)['last_profile']
        for i in range(len(self.users)):
            if(self.users[i]['id'] == id):
                self.users[i]['disliked'].append(disliked_id)
    
    def getUsers(self):
        return self.users
    
    def getChatIDs(self):
        data = []
        for i in range(len(self.users)):
            data.append(self.users[i]['id'])

    def addUser(self, user):
        self.users.append(user)
    
    def removeUser(self, id):
        for i in range(len(self.users)):
            if self.users[i]['id'] == id:
                os.remove('profiles/'+str(self.users[i]['id'])+'.json')
                self.users.remove(self.users[i])

    def getUserByID(self, id):
        for i in range(len(self.users)):
            if(self.users[i]['id'] == id):
                return self.users[i]
        return None
    
    def updateUserData(self, id, key, value):
        for i in range(len(self.users)):
            if(self.users[i]['id'] == id):
                self.users[i][key] = value
        self.saveUser(id)
