
from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model

import uuid
from app.config import get_settings
from .extractors import extract_video_id
from .exceptions import InvalidYoutubeVideoUrlException, VideoAlreadyAddedException
from app.users.models import User
from app.users.exceptions import InvalidUserIDException


settings = get_settings()


class Video(Model):
    __keyspace__ = settings.keyspace
    host_id = columns.Text(primary_key=True) #Youtube, Vimeo
    db_id = columns.UUID(primary_key=True, default=uuid.uuid1())
    host_service = columns.Text(default='Youtube')
    url = columns.Text()
    user_id = columns.UUID()
    
    def __str__(self):
        return self.__repr__()
    
    def __repr__(self):
        return f"Video(host_id={self.host_id}, host_service={self.host_service})"
    
    def as_data(self):
        return {f"{self.host_service}_id": self.host_id, "path": self.path}
    
    @property
    def path(self):
        return f"/videos/{self.host_id}"
    
    @staticmethod
    def add_video(url, user_id=None):
        host_id = extract_video_id(url)
        
        if host_id is None:
            raise InvalidYoutubeVideoUrlException("Invalid Youtube Video Url")
        
        user_exists = User.check_exists(user_id)        
        if user_exists is None:
            raise InvalidUserIDException("Invalid user_id")
        
        q = Video.objects.allow_filtering().filter(host_id=host_id, user_id=user_id)
        
        if q.count() != 0:
            raise VideoAlreadyAddedException("Video already added")
        return Video.create(host_id=host_id, user_id=user_id, url=url)
    
    