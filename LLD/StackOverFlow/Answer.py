from datetime import datetime
from Vote import Vote, Votable
from Comment import Commentable


class Answer(Commentable, Votable):
    def __init__(self, auther, question, content):
        self.id = id(self)
        self.author = auther
        self.question = question
        self.content = content
        self.votes = []
        self.comments = []
        self.creation_date = datetime.now()
        self.is_accepted = False
        
    
    def vote(self, user, value):
        if value not in [-1, 1]:
            raise ValueError("Vote value must be -1 or 1")
        for v in self.votes:
            if v.user == user:
                raise ValueError("User has already voted on this answer")
        vote = Vote(user, value)
        self.votes.append(vote)
        self.author.update_reputation(value *10) # +10 for upvote, -10 for downvote
    
    def get_vote_count(self):
        return sum(v.value for v in self.votes)
    
    def add_comment(self, comment):
        self.comments.append(comment)
    
    def get_comments(self):
        return self.comments.copy()
    
    def accept(self):
        if self.is_accepted:
            raise ValueError("This answer is already accepted")
        self.is_accepted = True
        self.author.update_reputation(15) # +15 for accepting an answer