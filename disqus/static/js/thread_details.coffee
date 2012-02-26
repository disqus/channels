class Details

    constructor: ->

        this.scrollBottom()
        $('.new-reply textarea').autoResize(
            maxHeight: 84
            minHeight: 28
        ).focus()

        $('#message').keydown (e) =>
            if e.which == 13 and not e.shiftKey
                this.submit()
                false

    submit: ->
        $('form')[0].submit()

    scrollBottom: ->
        $('body').animate scrollTop: $(document).height(), "slow"


$(document).ready () ->
    new Details()
