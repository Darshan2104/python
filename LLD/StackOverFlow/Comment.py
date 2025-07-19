from abc import ABC, abstractmethod
from datetime import datetime

class Comment:
    def __init__(self, author, content):
        self.id = id(self)
        self.author = author
        self.content = content
        self.creation_date = datetime.now()


class Commentable(ABC):
    @abstractmethod
    def add_comment(self, commnet: Comment):
        pass

    @abstractmethod
    def get_comments(self):
        pass