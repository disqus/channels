from flaskext.wtf import Form, Required, TextField, TextAreaField


class NewThreadForm(Form):
    subject = TextField('Subject', [Required()])


class NewPostForm(Form):
    message = TextAreaField('Message', [Required()])
