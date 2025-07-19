from datetime import datetime
from Vote import Vote, Votable
from Comment import Comment, Commentable
from Tag import Tag

class Question(Votable, Commentable):
    def __init__(self, author, title, body, tags):
        self.id = id(self)
        self.author = author
        self.title = title
        self.content = body
        self.tags = [Tag(tag) for tag in tags]
        self.creation_date = datetime.now()
        self.is_answered = False
        self.answers = []
        self.votes = []
        self.comments = []
    
    def add_answer(self, answer):
        if answer not in self.answers:
            self.answers.append(answer)
            self.is_answered = True if len(self.answers) > 0 else False
    
    def vote(self, user, value:int):
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
    
    def add_comment(self, comment:Comment):
        self.comments.append(comment)
    
    def get_comments(self) -> list[Comment]:
        return self.comments.copy()
