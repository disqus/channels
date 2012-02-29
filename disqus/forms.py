"""
disqus.forms
~~~~~~~~~~~~~~~

:copyright: (c) 2012 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

from flask import request
from flaskext.wtf import Form, Required, TextField, TextAreaField, ValidationError
from flaskext.wtf import validators


class ReferrerCheckForm(Form):
    def validate_on_submit(self, *args, **kwargs):
        referrer = request.environ.get('HTTP_REFERER')
        if not referrer.startswith(request.host_url):
            raise ValidationError('Invalid referrer')
        return super(ReferrerCheckForm, self).validate_on_submit(*args, **kwargs)


class NewThreadForm(ReferrerCheckForm):
    subject = TextField('Subject', [Required()])


class NewPostForm(ReferrerCheckForm):
    message = TextAreaField('Message', [Required(), validators.Length(min=2)])
