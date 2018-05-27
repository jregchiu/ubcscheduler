from app import db
from sqlalchemy.dialects import postgresql as pg

class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.Text, index=True, unique=True, nullable=False)
    activities = db.Column(pg.ARRAY(db.Text), nullable=False)
    sections = db.relationship('Section', backref='course', lazy=True)

    def __repr__(self):
        return '<Course {}>'.format(self.code)

class Section(db.Model):
    __tablename__ = 'sections'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    year = db.Column(db.Integer, index=True, nullable=False)
    session = db.Column(db.Text, index=True, nullable=False)
    code = db.Column(db.Text, nullable=False)
    status = db.Column(db.Text)
    activity = db.Column(db.Text, nullable=False)
    term = db.Column(pg.ARRAY(db.Integer), index=True, nullable=False)
    days = db.Column(pg.ARRAY(db.Text), index=True, nullable=False)
    start = db.Column(db.Time, index=True, nullable=False)
    end = db.Column(db.Time, index=True, nullable=False)

    def __repr__(self):
        return '<Section {}>'.format(self.code)
