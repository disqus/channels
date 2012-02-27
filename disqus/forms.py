"""
disqus.forms
~~~~~~~~~~~~~~~

:copyright: (c) 2012 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

from flaskext.wtf import Form, Required, TextField, TextAreaField


class NewThreadForm(Form):
    subject = TextField('Subject', [Required()])


class NewPostForm(Form):
    message = TextAreaField('Message', [Required()])
