class ListView extends Backbone.View
    el: '.post-list'

    initialize: ->

        _.bindAll @

        @collection = new PostList
        @collection.bind 'add', @appendPost
        @render()
        @scrollBottom()

    render: ->
        @$el.append '<ul class="post-list"></ul>'

    appendPost: (post) ->
        post_view = new PostView model: post

        @$el.append post_view.render().el

    addPost: ->
        post = new Post
        @collection.add post
        @scrollBottom()

    scrollBottom: ->
        $('body').animate scrollTop: $(document).height(), 0


class PostView extends Backbone.View
    tagName: 'li'
    className: 'post'
    template: _.template $('#post-template').html()

    initialize: ->
        _.bindAll @

    render: ->
        @$el.html @template @model.toJSON()
        @

class Post extends Backbone.Model

    defaults:
        message: 'omg'
        createdAt: "shrug"
        name: "matt"
        avatar: "http://mediacdn.disqus.com/uploads/users/843/7354/avatar92.jpg?1330244831"


class PostList extends Backbone.Collection

    model: Post

$(document).ready () ->
    window.list_view = new ListView

    $('.new-reply textarea').autoResize(
        maxHeight: 84
        minHeight: 28
        onAfterResize: () =>
            $('.conversation-stream').css('padding-bottom', $('.new-reply').height() + 10)
            list_view.scrollBottom()
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

