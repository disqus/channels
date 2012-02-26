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


class PostView extends Backbone.View
    el: $ '.conversation-stream'

    initialize: ->

        _.bindAll @

        @collection = new PostList
        @collection.bind 'add', @appendPost
        @render()

    render: ->
        $(@el).append '<ul class="post-list"></ul>'

    appendPost: ->
        $('.post-list').append "<li>Hi!</li>"

    addPost: ->
        post = new Post
        @collection.add post


class Post extends Backbone.Model

    defaults:
        message: 'omg'

class PostList extends Backbone.Collection

    model: Post

$(document).ready () ->
    window.postView = new PostView
    new Details()
