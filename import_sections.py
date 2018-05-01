from section import Section
from json import loads
from base import Session, engine, Base

Base.metadata.create_all(engine)

session = Session()

with open('sample_data/cpsc2018s.jl') as f:
    for line in f:
        s = loads(line)
        section = Section(s['course'], s['year'], s['session'], s['code'], s.get('status'), s['activity'], s['term'], s['days'], s['start'], s['end'])
        session.add(section)

session.commit()
session.close()
