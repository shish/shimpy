from .meta import Base, DBSession

from .post import Post as Image, Tag, PostBan, Comment, Alias, UnTag, map_post_tag
from .user import User, PrivateMessage, IPBan
from .wiki import WikiPage
