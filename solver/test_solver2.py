from json import loads
from ortools.constraint_solver import pywrapcp

def main():
    terms = ('1', '2')
    days = ('Mon', 'Tue', 'Wed', 'Thu', 'Fri')
    hours = ('7:00', '7:30', '8:00', '8:30', '9:00', '9:30', '10:00', '10:30', '11:00', '11:30', '12:00', '12:30', '13:00', '13:30', '14:00', '14:30', '15:00', '15:30', '16:00', '16:30', '17:00', '17:30', '18:00', '18:30', '19:00', '19:30', '20:00', '20:30', '21:00', '21:30', '22:00', '22:30')
    section_keys = ('course', 'activity', 'term', 'days', 'start', 'end')
    filters = ('Waiting List')
    long_weekends = ('Mon', 'Wed', 'Fri')

    courses_to_take = ('CPSC 310', 'CPSC 304')

    # read in course data
    courses = {}
    sections = {}
    with open('sample_data/cpsc2018w.jl') as f:
        for jsonline in f:
            c = loads(jsonline)
            code = c['code']
            if code in courses_to_take:
                activity_set = set()
                courses[code] = c
                for s in c['sections']:
                    if all (k in s for k in section_keys):
                        if s['activity'] not in filters:
                            sections[s['code']] = s
                            activity_set.add(s['activity'])
                            del s['code']
                c['activities'] = activity_set
                del c['code']
                del c['sections']

    # creates the constraint solver
    solver = pywrapcp.Solver('test_schedule_courses2')

    # create the variables
    solver_sections = {}
    for s in sections:
        solver_sections[s] = solver.BoolVar('{}'.format(s))
    solver_sections_flat = [solver_sections[s] for s in sections]

    # long weekend constraint
    for s in {s: sections[s] for s in sections if any (d in sections[s]['days'] for d in long_weekends)}:
        solver.Add(solver_sections[s] == 0)

    # create the constraints
    term_day_time = {}
    for t in terms:
        for d in days:
            for h in hours:
                term_day_time[(t, d, h)] = solver.IntVar(0, len(sections), 'term {0}, {1}, {2}'.format(t, d, h))
                sections_to_sum = {s: sections[s] for s in sections if t in sections[s]['term'] and d in sections[s]['days'] and h in [hr for hr in hours if hours.index(hr) >= hours.index(sections[s]['start']) and hours.index(hr) < hours.index(sections[s]['end'])]}
                solver.Add(term_day_time[(t, d, h)] == solver.Sum([solver_sections[s] for s in sections_to_sum]))
                solver.Add(term_day_time[(t, d, h)] >= 0)
                solver.Add(term_day_time[(t, d, h)] <= 1)
            solver.Add(solver.Sum([term_day_time[(t, d, h)] for h in hours]) >= 0)
            solver.Add(solver.Sum([term_day_time[(t, d, h)] for h in hours]) <= len(hours))
        for h in hours:
            solver.Add(solver.Sum([term_day_time[(t, d, h)] for d in days]) >= 0)
            solver.Add(solver.Sum([term_day_time[(t, d, h)] for d in days]) <= len(days))

    course_activity = {}
    for c in courses:
        activities = courses[c]['activities']
        for a in activities:
            course_activity[(c, a)] = solver.IntVar(0, len(sections), '{0}, {1}'.format(c, a))
            sections_to_sum = {s: sections[s] for s in sections if c == sections[s]['course'] and a == sections[s]['activity']}
            solver.Add(course_activity[(c, a)] == solver.Sum([solver_sections[s] for s in sections_to_sum]))
            solver.Add(course_activity[(c, a)] >= 0)
            solver.Add(course_activity[(c, a)] <= 1)
        solver.Add(solver.Sum([course_activity[(c, a)] for a in activities]) == len(courses[c]['activities']))

    # create the decision builder
    db = solver.Phase(solver_sections_flat, solver.CHOOSE_FIRST_UNBOUND, solver.ASSIGN_MIN_VALUE)

    # create the solution collector
    solution = solver.Assignment()
    solution.Add(solver_sections_flat)
    collector = solver.AllSolutionCollector(solution)

    # call the solver
    solver.Solve(db, [collector])
    print('Solutions found:', collector.SolutionCount())
    print('Time:', solver.WallTime(), 'ms', '\n')

    # print solutions
    for sol in range(collector.SolutionCount()):
        print('Solution:', sol)
        for s in sections:
            if collector.Value(sol, solver_sections[s]) == 1:
                print(s)
        print()

if __name__ == "__main__":
    main()
