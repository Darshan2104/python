from typing import List, Dict
from User import User
from Question import Question
from Answer import Answer
from Tag import Tag


# What all functionalities are we providing to the user?
class StackOvertFlow:
    def __init__(self):
        self.users: Dict[int, User] = {}
        self.questions: Dict[int, Question] = {}
        self.answers: Dict[int, Answer] = {}
        self.tags: Dict[str, Tag] = {}

    
    def create_user(self, username, email):
        user_id = len(self.users) + 1
        user = User(user_id, username, email)
        self.users[user_id] = user
        return user

    def ask_question(self, user:User, title, content, tags):
        question : Question = user.ask_question(title, content, tags)
        self.questions[question.id] = question
        for tag in question.tags:
            self.tags.setdefault(tag.name, tag)
        return question

    def answer_question(self, user:User, question, content):
        answer :Answer = user.answer_question(question, content)
        self.answers[answer.id] = answer
        return answer
        
    def add_comment(self, user:User, commentable, content):
        # Here Commentable could be a Question or Answer
        return user.comment_on(commentable, content)


    def vote_question(self, user, question:Question, value):
        question.vote(user, value)

    def vote_answer(self, user, answer:Answer, vote):
        answer.vote(user, vote)

    def accpet_answer(self, answer:Answer):
        answer.accept()
        pass

    def search_question(self, query):
        return [q for q in self.questions.values() if 
                query.lower() in q.title.lower() or
                query.lower() in q.content.lower() or
                any(query.lower() == tag.name.lower() for tag in q.tags)]

    def get_question_by_user(self, user:User):
        return user.questions
    
    def get_user(self, user_id):
        return self.users.get(user_id)

    def get_question(self, question_id):
        return self.questions.get(question_id)
    
    def get_answer(self, answer_id):
        return self.answers.get(answer_id)
    
    def get_tag(self, tag_name):
        return self.tags.get(tag_name)
    