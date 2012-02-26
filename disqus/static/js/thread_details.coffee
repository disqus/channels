class Details

    constructor: ->

        this.scrollBottom()
        $('.new-reply textarea').autoResize(
            maxHeight: 84
            minHeight: 28
            onAfterResize: () =>
                $('.conversation-stream').css('padding-bottom', $('.new-reply').height() + 10)
                this.scrollBottom()
        ).focus()

        $('#message').keydown (e) =>
            if e.which == 13 and not e.shiftKey
                $('.new-reply form').submit()
                false

        $('.new-reply form').submit () ->
            button = $('button[type=submit]', this)
            setTimeout () =>
                button.attr 'disabled', 'disabled'
            , 50

            if button.attr 'disabled'
                false

    scrollBottom: ->
        $('body').animate scrollTop: $(document).height(), 0


$(document).ready () ->
    new Details()
