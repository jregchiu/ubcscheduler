from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired

class CoursesForm(FlaskForm):
    courses = TextAreaField('Courses', validators=[DataRequired()])
    submit = SubmitField('Generate schedules')
