from sqlalchemy import Column, String, Integer, ARRAY
from base import Base

class Section(Base):
    __tablename__ = 'sections'

    id = Column(Integer, primary_key=True)
    course = Column(String)
    year = Column(String)
    session = Column(String)
    code = Column(String, unique=True)
    status = Column(String)
    activity = Column(String)
    term = Column(ARRAY(String))
    days = Column(ARRAY(String))
    start = Column(String)
    end = Column(String)

    def __init__(self, course, year, session, code, status, activity, term, days, start, end):
        self.course = course
        self.year = year
        self.session = session
        self.code = code
        self.status = status
        self.activity = activity
        self.term = term
        self.days = days
        self.start = start
        self.end = end
