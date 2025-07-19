import uuid
from abc import ABC, abstractmethod
class Vote:
    def __init__(self,user, value):
        self.vote_id = str(uuid.uuid4())
        self.user = user
        self.value = value
    

class Votable(ABC):
    @abstractmethod
    def vote(self, user, value):
        pass

    @abstractmethod
    def get_vote_count(self):
        pass
