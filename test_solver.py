from json import load
from ortools.constraint_solver import pywrapcp

def main():
    terms = ('1', '2')
    days = ('Mon', 'Tue', 'Wed', 'Thu', 'Fri')
    hours = ('7:00', '7:30', '8:00', '8:30', '9:00', '9:30', '10:00', '10:30', '11:00', '11:30', '12:00', '12:30', '13:00', '13:30', '14:00', '14:30', '15:00', '15:30', '16:00', '16:30', '17:00', '17:30', '18:00', '18:30', '19:00', '19:30', '20:00', '20:30', '21:00', '21:30', '22:00', '22:30')
    activities_filter = ('Lecture', 'Laboratory', 'Tutorial', 'Seminar', 'Discussion')
    filters = ('Full', 'Waiting List')

    courses_to_take = ('CPSC 221', 'CPSC 213')

    # read in course data
    with open('sample_data/cpsc18s.json') as f:
        all_courses = load(f)

    courses = {}
    for c in [c for c in all_courses if c['code'] in courses_to_take]:
        sections = {}
        activity_set = set()
        courses[c['code']] = c
        for s in c['sections']:
            if s['activity'] in activities_filter:
                # if ('status' in s and s['status'] not in filters) or 'status' not in s:
                    sections[s['code']] = s
                    activity_set.add(s['activity'])
                    del s['code']
                    del s['course']
        assert len(activity_set) == int(c['activities'])
        c['sections'] = sections
        c['activity_set'] = activity_set
        del c['code']

    # creates the constraint solver
    solver = pywrapcp.Solver('test_schedule_courses')

    # create variables
    arr = {}
    for c in courses:
        for s in courses[c]['sections']:
            for t in terms:
                for d in days:
                    for h in hours:
                        arr[(s, t, d, h)] = solver.BoolVar('{0}, {1}, {2}, {3}'.format(s, t, d, h))
    arr_flat = [arr[(s, t, d, h)] for c in courses for s in courses[c]['sections'] for t in terms for d in days for h in hours]

    # create constraints
    for t in terms:
        for d in days:
            for h in hours:
                solver.Add(solver.Sum(arr[(s, t, d, h)] for c in courses for s in courses[c]['sections']) >= 0)
                solver.Add(solver.Sum(arr[(s, t, d, h)] for c in courses for s in courses[c]['sections']) <= 1)

    for c in courses:
        sections = courses[c]['sections']
        for s in sections:
            section = sections[s]
            section_hours = [h for h in hours if hours.index(h) >= hours.index(section['start']) and hours.index(h) < hours.index(section['end'])]
            for t in terms:
                for d in days:
                    for h in hours:
                        if t not in section['term'] or d not in section['days'] or h not in section_hours:
                            solver.Add(arr[(s, t, d, h)] == False)
            for t in terms:
                for d in days:
                    solver.Add(solver.Max(solver.Sum(arr[(s, t, d, h)] for h in hours) == len(section_hours), solver.Sum(arr[(s, t, d, h)] for h in hours) == 0) == 1)
                for h in hours:
                    solver.Add(solver.Max(solver.Sum(arr[(s, t, d, h)] for d in days) == len(section['days']), solver.Sum(arr[(s, t, d, h)] for d in days) == 0) == 1)
        '''need to figure out if the below constraints are correct
        for a in activities:
            section = next (iter ({s: sections[s] for s in sections if sections[s]['activity'] == a}.values()))
            section_hours = [h for h in hours if hours.index(h) >= hours.index(section['start']) and hours.index(h) < hours.index(section['end'])]
            solver.Add(solver.Sum(arr[(c, s, a, t, d, h)] for s in sections for t in terms for d in days for h in hours) == len(section_hours) * len(section['days']))
        solver.Add(solver.Sum(arr[(c, s, a, t, d, h)] for s in sections for a in activities for t in terms for d in days for h in hours) == courses[c]['activities'] * ())
        '''

    '''
    course_activities = {}
    for c in courses:
        sections = courses[c]['sections']
        activities = courses[c]['activity_set']
        for a in activities:
            course_activities[(c, a)] = solver.BoolVar('{0}, {1}'.format(c, a))
            sections_activities = {s: sections[s] for s in sections if sections[s]['activity'] == a}
            section = next (iter (sections_activities.values()))
            section_hours = [h for h in hours if hours.index(h) >= hours.index(section['start']) and hours.index(h) < hours.index(section['end'])]
            solver.Add(solver.Sum(arr[(s, t, d, h)] for s in sections_activities for t in terms for d in days for h in hours) == len(section_hours) * len(section['days']))
            solver.Add(course_activities[(c, a)] == True)
        solver.Add(solver.Sum(course_activities[(c, a)] for a in activities) == int(courses[c]['activities']))
    '''
    
    # create the decision builder
    db = solver.Phase(arr_flat, solver.CHOOSE_FIRST_UNBOUND, solver.ASSIGN_MIN_VALUE)

    # create the solution collector
    solution = solver.Assignment()
    solution.Add(arr_flat)
    collector = solver.AllSolutionCollector(solution)

    # call the solver
    solver.Solve(db, [collector])
    print('Solutions found:', collector.SolutionCount())
    print('Time:', solver.WallTime(), 'ms')

    # print Solutions
    for sol in range(collector.SolutionCount()):
        print('Solution:', sol, '\n')
        for c in courses:
            for s in courses[c]['sections']:
                print(s)
                for d in days:
                    for h in hours:
                        print(collector.Value(sol, arr[(s, t, d, h)]))

if __name__ == "__main__":
    main()
