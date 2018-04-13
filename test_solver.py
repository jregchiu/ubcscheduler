from json import load
from ortools.constraint_solver import pywrapcp

def main():
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
    hours = ['7:00', '7:30', '8:00', '8:30', '9:00', '9:30', '10:00', '10:30', '11:00', '11:30', '12:00', '12:30', '13:00', '13:30', '14:00', '14:30', '15:00', '15:30', '16:00', '16:30', '17:00', '17:30', '18:00', '18:30', '19:00', '19:30', '20:00', '20:30', '21:00', '21:30', '22:00', '22:30']
    activities = ['Lecture', 'Laboratory', 'Seminar', 'Tutorial', 'Discussion']

    courses_to_take = ['CPSC 221', 'CPSC 213']

    # read in course data
    with open('sample_data/cpsc18s.json') as f:
        all_courses = load(f)

    courses_list = [c for c in all_courses if c['code'] in courses_to_take]
    sections = {}
    courses = {}
    num_activities = 0
    for c in courses_list:
        num_activities += int(c['activities'])
        courses[c['code']] = c
        for s in c['sections']:
            sections[s['code']] = s

    # creates the constraint solver
    solver = pywrapcp.Solver('test_schedule_courses')

    # create variables
    arr = {}
    for s in sections:
        for d in days:
            for h in hours:
                arr[(s, d, h)] = solver.BoolVar('{0}, {1}, {2}'.format(s, d, h))
    arr_flat = [arr[(s, d, h)] for s in sections for d in days for h in hours]

    # create constraints
    for d in days:
        for h in hours:
            solver.Add(solver.Sum(arr[(s, d, h)] for s in sections) >= 0)
            solver.Add(solver.Sum(arr[(s, d, h)] for s in sections) <= 1)

    for s in sections:
        section_hours = [h for h in hours if hours.index(h) >= hours.index(sections[s]['start']) and hours.index(h) < hours.index(sections[s]['end'])]
        for d in days:
            for h in hours:
                if d not in sections[s]['days'] or h not in section_hours:
                    solver.Add(arr[(s, d, h)] == False)
            solver.Add(solver.Max(solver.Sum(arr[(s, d, h)] for h in hours) == len(section_hours), solver.Sum(arr[(s, d, h)] for h in hours) == 0) == 1)
        for h in hours:
            solver.Add(solver.Max(solver.Sum(arr[(s, d, h)] for d in days) == len(sections[s]['days']), solver.Sum(arr[(s, d, h)] for d in days) == 0) == 1)

    ''' WHY DOESNT THIS WORK
    course_activities = {}
    for c in courses:
        for a in activities:
            course_activities[(c, a)] = solver.BoolVar('{0}, {1}'.format(c, a))
            solver.Add(course_activities[(c, a)] == solver.Max([solver.Sum(arr[(s, d, h)] for s in sections for d in days for h in hours) == (len([h for h in hours if hours.index(h) >= hours.index(sections[s]['start']) and hours.index(h) < hours.index(sections[s]['end'])]) * len(sections[s]['days']) for s in [section for section in sections if sections[s]['activity'] == a and sections[s]['course'] == c])]))
        solver.Add(solver.Sum(course_activities[(c, a)] for a in activities) == courses[c]['activities'])
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
    print()

    # display a few solutions


if __name__ == "__main__":
    main()
