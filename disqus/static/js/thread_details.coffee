class ParticipantsView extends Backbone.View
    el: '.user-list'

    initialize: ->

        _.bindAll @

        @collection = new UserList
        @collection.bind 'add', @appendUser

    appendUser: (user) ->
        user_view = new UserView model: user

        um = user_view.render()
        @$el.append um.el
        $('img', um.$el).tooltip()

    addUser: (user) ->
        @collection.add user


class UserView extends Backbone.View
    tagName: 'li'
    template: _.template $('#participant-template').html()

    initialize: ->
        _.bindAll @

    render: ->
        @$el.html @template @model.toJSON()
        @

window.User = class User extends Backbone.Model

    defaults:
        name: "matt"
        avatar: "http://mediacdn.disqus.com/uploads/users/843/7354/avatar92.jpg?1330244831"
        profileLink: "http://example.com"

class UserList extends Backbone.Collection

    model: User

class ListView extends Backbone.View
    el: '.post-list'

    initialize: ->

        _.bindAll @

        @collection = new PostList
        @collection.bind 'add', @appendPost

    appendPost: (post) ->
        post_view = new PostView model: post

        @$el.append post_view.render().el

    addPost: (post) ->
        scrolled = @isAtBottom()
        @collection.add post
        if scrolled
            @scrollBottom()

    scrollBottom: ->
        $('body').animate scrollTop: $(document).height(), 0

    isAtBottom: ->
        $(window).scrollTop() + $(window).height() == $(document).height()


class PostView extends Backbone.View
    tagName: 'li'
    className: 'post'
    template: _.template $('#post-template').html()

    initialize: ->
        _.bindAll @

    render: ->
        @$el.html @template @model.toJSON()
        @

window.Post = class Post extends Backbone.Model

    defaults:
        message: 'omg'
        createdAtISO: "shrug"
        name: "matt"
        avatar: "http://mediacdn.disqus.com/uploads/users/843/7354/avatar92.jpg?1330244831"

    initialize: ->
        @set 'createdAtSince', Disqus.prettyDate(@get 'createdAtISO' )


class PostList extends Backbone.Collection

    model: Post


$(document).ready () ->
    window.list_view = new ListView
    window.participants_view = new ParticipantsView

    $('#message').keydown (e) =>
        if e.which == 13 and not e.shiftKey
            $('.new-reply form').submit()
            false

    $('.new-reply form').submit () ->
        if $('textarea', this).val().length <= 2
            return false
        button = $('button[type=submit]', this)

        if button.attr 'disabled'
            return false

        button.attr 'disabled', 'disabled'

        $.ajax
            url: $(this).attr 'action'
            data: $(this).serialize()
            type: 'POST'
            success: (data, status) =>
                $(':input', this).not(':button, :submit, :reset, :hidden').val('')
            complete: (jqxhr, status) ->
                button.removeAttr 'disabled'

        false

    for post in initialPosts
        p = new Post(post)
        list_view.addPost(p)

    for user in initialParticipants
        p = new User user
        participants_view.addUser p

    $('.new-reply textarea').autoResize(
        maxHeight: 84
        minHeight: 28
        onAfterResize: () =>
            $('.conversation').css('padding-bottom', $('.new-reply').outerHeight())
            list_view.scrollBottom()
    ).focus()


    $.getScript(realtime_host + '/socket.io/socket.io.js')
    .done (script, status) ->
        socket = io.connect realtime_host

        socket.on channels.posts, (data) ->
            payload = JSON.parse data
            p = new Post payload.data
            console.log p
            if payload.event == 'add'
                list_view.addPost(p)
            else
                console.log payload

        socket.on channels.participants, (data) ->
            payload = JSON.parse data
            u = new User payload.data
            console.log u
            if payload.event == 'add'
                participants_view.addUser u
            else
                console.log payload

        socket.on 'connect', () ->
            socket.emit 'connect',
                channels: _.values channels
