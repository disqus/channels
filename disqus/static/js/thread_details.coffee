class Details

    constructor: ->

        $('#message').keydown (e) =>
            if e.which == 13 and not e.shiftKey
                this.submit()
                false

    submit: ->
        $('form')[0].submit()


$(document).ready () ->
    new Details()
