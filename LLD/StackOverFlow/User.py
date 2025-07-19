from datetime import datetime
from Question import Question
from Answer import Answer
from Comment import Comment
class User:
    def __init__(self, user_id, username, email):
        self.id = user_id 
        self.username = username
        self.email = email
        self.reputation  = 0
        self.questions = []
        self.answers = []
        self.comments = []
    
    def ask_question(self, title, content, tags):
        question = Question(self, title, content, tags)
        self.questions.append(question)
        self.reputation += 5  # Assuming asking a question gives reputation
        return question
    
    def answer_question(self, question, content):
        answer = Answer(self, question, content)
        self.answers.append(answer)
        self.update_reputation(10)  # Assuming answering a question gives reputation
        return answer
    
    def comment_on(self, commentable, content):
        # Assuming comments are stored in a list
        comment = Comment(self, content)
        self.comments.append(comment)
        # Here Commnetable could be a Question or Answer
        commentable.add_comment(comment)
        self.update_reputation(5)  # Assuming commenting gives reputation
        return comment
    
    def update_reputation(self, points):
        self.reputation += points
        self.reputation = max(0, self.reputation)  # Ensure reputation doesn't go below 0