from sqlalchemy import Column, String, Integer, ARRAY
from base import Base

class Section(Base):
    __tablename__ = 'sections'

    id = Column(Integer, primary_key=True)
    course = Column(String, nullable=False)
    year = Column(String, nullable=False)
    session = Column(String, nullable=False)
    code = Column(String, nullable=False)
    status = Column(String)
    activity = Column(String, nullable=False)
    term = Column(ARRAY(String), nullable=False)
    days = Column(ARRAY(String), nullable=False)
    start = Column(String, nullable=False)
    end = Column(String, nullable=False)

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
