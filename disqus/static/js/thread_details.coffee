class Details

    constructor: ->

        this.scrollBottom()

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
