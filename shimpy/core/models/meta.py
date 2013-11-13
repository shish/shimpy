from sqlalchemy import (
    Table,
    Column,
    ForeignKey,

    Integer,
    Text,
    String,
    Unicode,
    DateTime,
    Boolean,

    func,
    desc,
    )
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship, backref
import sqlalchemy.types as types

from shimpy.core.database import Base, Session as DBSession



class BooleanYN(types.TypeDecorator):
    '''Stores a boolean value as 'Y' or 'N',
    because mysql lacks native boolean...
    '''

    impl = types.Boolean

    def process_bind_param(self, value, dialect):
        return (u"Y" if value else u"N")

    def process_result_value(self, value, dialect):
        return (value == u"Y")
