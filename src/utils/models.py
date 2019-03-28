import datetime

# from flask_sqlalchemy import SQLAlchemy

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class RegisteredUser(db.Model):
    __tablename__ = 'registereduser'

    user_id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String())
    email = db.Column(db.String())
    password = db.Column(db.String())
    fullname = db.Column(db.String())
    created_on = db.Column(db.DateTime, default =  datetime.datetime.now())
    updated_on = db.Column(db.DateTime, default =  datetime.datetime.now())
    status_enabled = db.Column(db.Boolean(), default = True)    

    def __init__(self,username,email,password,fullname):
        self.username = username
        self.email = email
        self.password = password
        self.fullname = fullname

    # buat ngereturn user id nya
    def __repr__(self):
        return '<user id {}>'.format(self.user_id)

    def serialise(self):
        return {
            'user_id' : self.user_id,
            'username' : self.username,
            'email' : self.email,
            'password' : self.password,
            'fullname' : self.fullname,
            'status_enabled' : self.status_enabled
        }

    def returnToUser(self):
        return {
            # 'user_id' : self.user_id,
            'username' : self.username,
            'email' : self.email,
            # 'password' : self.password,
            'fullname' : self.fullname,
            # 'status_enabled' : self.status_enabled
        }
    

###############################################

class Quiz(db.Model):
    __tablename__ = 'quiz'

    quiz_id = db.Column(db.Integer, primary_key = True)
    quiz = db.Column(db.String())
    quiz_category = db.Column(db.String())
    creator_id = db.Column(db.Integer(), db.ForeignKey('registereduser.user_id'))
    created_on = db.Column(db.DateTime, default =  datetime.datetime.now())
    updated_on = db.Column(db.DateTime, default =  datetime.datetime.now())
    status_enabled = db.Column(db.Boolean(), default = True)
    # question_list = db.Column(db.Integer())
    question = db.relationship('Question',cascade="all,delete", backref='Quiz', lazy=True)


    def __init__(self,quiz,quiz_category,creator_id):
        self.quiz = quiz
        self.quiz_category = quiz_category
        self.creator_id = creator_id
        # self.question_list = question_list

    # buat ngereturn quiz id nya
    def __repr__(self):
        return '<quiz id {}>'.format(self.quiz_id)

    def serialise(self):
        return {
            'quiz_id' : self.quiz_id,
            'quiz' : self.quiz,
            'quiz_category' : self.quiz_category,
            'creator_id' : self.creator_id,
            'status_enabled' : self.status_enabled,
            'question_list' : [{'question_id': e.question_id, 'question' : e.question, 'status_enabled': e.status_enabled} for e in self.question]
        }

    # def allQuizInfo(self):
    #     print(self.question)
    #     questionList = []
    #     for e in self.question:
    #         e = Question()
    #         questionList.append(e)
    #     print(questionList)
    #     return {
    #         'quiz_id' : self.quiz_id,
    #         'quiz' : self.quiz,
    #         'quiz_category' : self.quiz_category,
    #         'creator_id' : self.creator_id,
    #         'status_enabled' : self.status_enabled,
    #         'question_list' : [{e.serialise()} for e in self.question]        
    #     }

###############################################

class Question(db.Model):
    __tablename__ = 'question'

    question_id = db.Column(db.Integer, primary_key = True)
    quiz_id = db.Column(db.Integer(), db.ForeignKey('quiz.quiz_id'), nullable= False)
    question = db.Column(db.String())
    answer = db.Column(db.String())
    created_on = db.Column(db.DateTime, default =  datetime.datetime.now())
    updated_on = db.Column(db.DateTime, default =  datetime.datetime.now())
    status_enabled = db.Column(db.Boolean(), default = True)
    # options = db.Column(db.String())
    options = db.relationship('Options',cascade="all,delete", backref='Question', lazy=True)

    def __init__(self,quiz_id,question,answer):
        self.quiz_id = quiz_id
        self.question = question
        self.answer = answer
        # self.options = options

    # buat ngereturn question id nya
    def __repr__(self):
        return '<question id {}>'.format(self.question_id)

    def serialise(self):
        return {
            'question_id' : self.question_id,
            'quiz_id' : self.quiz_id,
            'question' : self.question,
            'answer' : self.answer,
            'status_enabled' : self.status_enabled,
            'options' : [{'option_id': e.option_id, 'option': e.option} for e in self.options]
        }
        

    
###############################################
class Options(db.Model):
    __tablename__ = 'options'

    option_id = db.Column(db.Integer, primary_key = True)
    question_id = db.Column(db.Integer(), db.ForeignKey('question.question_id'), nullable = False)
    option = db.Column(db.String())
    created_on = db.Column(db.DateTime, default =  datetime.datetime.now())
    updated_on = db.Column(db.DateTime, default =  datetime.datetime.now())
    status_enabled = db.Column(db.Boolean(), default = True)

    def __init__(self,question_id,option):
        self.question_id = question_id
        self.option = option

    # buat ngereturn question id nya
    def __repr__(self):
        return '<option id {}>'.format(self.option_id)

    def serialise(self):
        return {
            'option_id' : self.option_id,
            'question_id' : self.question_id,
            'option' : self.option,
            'status_enabled' : self.status_enabled
        }


###############################################

class Game(db.Model):
    __tablename__ = 'game'

    game_id = db.Column(db.Integer, primary_key = True)
    game_pin = db.Column(db.Integer())
    quiz_id = db.Column(db.Integer(), db.ForeignKey('quiz.quiz_id'), nullable = False)
    created_on = db.Column(db.DateTime, default =  datetime.datetime.now())
    status_enabled = db.Column(db.Boolean(), default = True)
    leaderboard = db.relationship('Leaderboard',cascade="all,delete", backref='Game', lazy=True)
    userscore = db.relationship('UserScore',cascade="all,delete", backref='Game', lazy=True)

    def __init__(self,game_pin,quiz_id):
        self.game_pin = game_pin
        self.quiz_id = quiz_id


    # buat ngereturn question id nya
    def __repr__(self):
        return '<game id {}>'.format(self.game_id)

    def serialise(self):
        return {
            'game_id' : self.game_id,
            'game_pin' : self.game_pin,
            'quiz_id' : self.quiz_id,
            # 'leaderboard': [{'username': e.username, 'score': e.score} for e in self.leaderboard],
            'leaderboard': {'userscore' : [{'username': e.username, 'score': e.score} for e in self.userscore]}
        }
        

    
###############################################


###############################################

class Leaderboard(db.Model):
    __tablename__ = 'leaderboard'

    leaderboard_id = db.Column(db.Integer, primary_key = True)
    quiz_id = db.Column(db.Integer(), db.ForeignKey('quiz.quiz_id'), nullable = False)
    game_id = db.Column(db.Integer(), db.ForeignKey('game.game_id'), nullable = False)
    created_on = db.Column(db.DateTime, default =  datetime.datetime.now())
    updated_on = db.Column(db.DateTime, default =  datetime.datetime.now())
    status_enabled = db.Column(db.Boolean(), default = True)
    userscore = db.relationship('UserScore',cascade="all,delete", backref='Leaderboard', lazy=True)

    def __init__(self,quiz_id, game_id):
        self.quiz_id = quiz_id
        self.game_id = game_id


    # buat ngereturn question id nya
    def __repr__(self):
        return '<leaderboard id {}>'.format(self.leaderboard_id)

    def serialise(self):
        userscore = [{'username': e.username, 'score': e.score} for e in self.userscore]
        userscore.sort(key = lambda x: x['score'], reverse=True)
        print(userscore[0]['score'])
        return {
            'leaderboard_id' : self.leaderboard_id,
            'quiz_id' : self.quiz_id,
            'game_id' : self.game_id,
            'status_enabled': self.status_enabled,
            'userscore' : userscore
        }

        
        


###############################################

class UserScore(db.Model):
    __tablename__ = 'userscore'

    userscore_id = db.Column(db.Integer, primary_key = True)
    leaderboard_id = db.Column(db.Integer(), db.ForeignKey('leaderboard.leaderboard_id'), nullable = False)
    game_id = db.Column(db.Integer(), db.ForeignKey('game.game_id'), nullable = False)
    created_on = db.Column(db.DateTime, default =  datetime.datetime.now())
    updated_on = db.Column(db.DateTime, default =  datetime.datetime.now())
    status_enabled = db.Column(db.Boolean(), default = True)
    username = db.Column(db.String())
    score = db.Column(db.Integer())

    def __init__(self,leaderboard_id, game_id, username,score):
        self.leaderboard_id = leaderboard_id
        self.game_id = game_id
        self.username = username
        self.score = score


    # buat ngereturn question id nya
    def __repr__(self):
        return '<userscore id {}>'.format(self.userscore_id)

    def serialise(self):
        return {
            'userscore_id' : self.userscore_id,
            'leaderboard_id' : self.leaderboard_id,
            'game_id' : self.game_id,
            'status_enabled': self.status_enabled,
            'username': self.username,
            'score': self.score
        }

    def getUsernameOnly(self):
        return self.username
        
