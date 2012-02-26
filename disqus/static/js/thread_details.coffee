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
                this.submit()
                false

    submit: ->
        $('form')[0].submit()

    scrollBottom: ->
        $('body').animate scrollTop: $(document).height(), 0


$(document).ready () ->
    new Details()
