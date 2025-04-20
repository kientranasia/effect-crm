from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField, TimeField, SubmitField
from wtforms.validators import DataRequired, Length
from app.models.interaction import Interaction

class InteractionForm(FlaskForm):
    type = SelectField('Type', validators=[DataRequired()],
                      choices=[(k, v) for k, v in Interaction.TYPE_CHOICES.items()])
    
    title = StringField('Title', validators=[DataRequired(), Length(max=255)])
    description = TextAreaField('Description')
    
    date = DateField('Date', validators=[DataRequired()])
    time = TimeField('Time', validators=[DataRequired()])
    
    status = SelectField('Status',
                        choices=[(k, v) for k, v in Interaction.STATUS_CHOICES.items()])
    
    outcome = TextAreaField('Outcome')
    next_steps = TextAreaField('Next Steps')
    
    submit = SubmitField('Save Interaction') 