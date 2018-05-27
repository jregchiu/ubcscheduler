from json import loads
from time import strptime
from app import create_app, db
from app.models import Course, Section

s = input('File to load: ')
app = create_app()
app.app_context().push()

courses = {}
with open(s) as f:
    for line in f:
        s = loads(line)
        if s['course'] not in courses:
            c = Course(code=s['course'], activities=[s['activity']])
            courses[s['course']] = c
        else:
            c = courses[s['course']]
            if s['activity'] not in c.activities:
                c.activities.append(s['activity'])
        sec = Section(course=c, year=int(s['year']), session=s['session'], code=s['code'], status=s.get('status'), activity=s['activity'], term=[int(t) for t in s['term']], days=s['days'], start=s['start'], end=s['end'])
        db.session.add(sec)

for c in courses.values():
    db.session.add(c)
db.session.commit()
