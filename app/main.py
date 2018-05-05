from flask import Blueprint, render_template, make_response
from datetime import datetime as dt
from app.forms import CoursesForm
from app.models import Course, Section
from ortools.constraint_solver import pywrapcp

terms = ('1', '2')
days = ('Mon', 'Tue', 'Wed', 'Thu', 'Fri')
hours = ('7:00', '7:30', '8:00', '8:30', '9:00', '9:30', '10:00', '10:30', '11:00', '11:30', '12:00', '12:30', '13:00', '13:30', '14:00', '14:30', '15:00', '15:30', '16:00', '16:30', '17:00', '17:30', '18:00', '18:30', '19:00', '19:30', '20:00', '20:30', '21:00', '21:30', '22:00', '22:30')

bp = Blueprint('main', __name__)

@bp.route('/', methods=['GET', 'POST'])
def index():
    results = []
    form = CoursesForm()
    if form.validate_on_submit():
        course_list = form.courses.data.splitlines()
        courses = []
        sections = []
        for c in course_list:
            search = c.split(': ')
            courses.extend(Course.query.filter_by(code=search[0]))
            sections.extend(Section.query.with_parent(Course.query.filter_by(code=search[0]).first()).filter(Section.term.any(search[1])).all())
        # create the constraint solver
        solver = pywrapcp.Solver('scheduler')
        # create the variables
        solver_sections = {}
        for s in sections:
            solver_sections[s.code] = solver.BoolVar('{}'.format(s.code))
        solver_sections_flat = [solver_sections[s.code] for s in sections]
        # create the constraints
        term_day_time = {}
        for t in terms:
            for d in days:
                for h in hours:
                    term_day_time[(t, d, h)] = solver.IntVar(0, len(sections), 'term {0}, {1}, {2}'.format(t, d, h))
                    sections_to_sum = [s for s in sections if t in s.term and d in s.days and dt.strptime(h, '%H:%M').time() >= s.start and dt.strptime(h, '%H:%M').time() < s.end]
                    solver.Add(term_day_time[(t, d, h)] == solver.Sum([solver_sections[s.code] for s in sections_to_sum]))
                    solver.Add(term_day_time[(t, d, h)] >= 0)
                    solver.Add(term_day_time[(t, d, h)] <= 1)
                solver.Add(solver.Sum([term_day_time[(t, d, h)] for h in hours]) >= 0)
                solver.Add(solver.Sum([term_day_time[(t, d, h)] for h in hours]) <= len(hours))
            for h in hours:
                solver.Add(solver.Sum([term_day_time[(t, d, h)] for d in days]) >= 0)
                solver.Add(solver.Sum([term_day_time[(t, d, h)] for d in days]) <= len(days))
        course_activity = {}
        for c in courses:
            for a in c.activities:
                course_activity[(c, a)] = solver.IntVar(0, len(sections), '{0}, {1}'.format(c, a))
                sections_to_sum = [s for s in sections if c == s.course and a == s.activity]
                solver.Add(course_activity[(c, a)] == solver.Sum([solver_sections[s.code] for s in sections_to_sum]))
                solver.Add(course_activity[(c, a)] >= 0)
                solver.Add(course_activity[(c, a)] <= 1)
            solver.Add(solver.Sum([course_activity[(c, a)] for a in c.activities]) == len(c.activities))
        # create the decision builder
        db = solver.Phase(solver_sections_flat, solver.CHOOSE_FIRST_UNBOUND, solver.ASSIGN_MIN_VALUE)
        # create the solution collector
        solution = solver.Assignment()
        solution.Add(solver_sections_flat)
        collector = solver.AllSolutionCollector(solution)
        # limit the number of solutions to 100
        solutions_limit = solver.SolutionsLimit(100)
        # call the solver
        solver.Solve(db, [solutions_limit, collector])
        # return solutions
        for sol in range(collector.SolutionCount()):
            solution = []
            for s in sections:
                if collector.Value(sol, solver_sections[s.code]) == 1:
                    solution.append(s.code)
            results.append(solution)
    return render_template('index.html', form=form, results=results)
