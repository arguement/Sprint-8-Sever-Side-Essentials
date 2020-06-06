from wtforms.validators import ValidationError

def check_end_date_greater_than_start(form, field):
    if not field.data or not form.start_date.data:
        return
    if field.data < form.start_date.data:
        raise ValidationError(f'{field.id} should be greater than {form.start_date.id}')