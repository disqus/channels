class ParticipantsView extends Backbone.View
    el: '.user-list'

    initialize: ->

        _.bindAll @

        @collection = new UserList
        @collection.bind 'add', @appendUser
        @collection.bind 'remove', @clearUser

    appendUser: (user) ->
        user_view = new UserView model: user

        um = user_view.render()
        $('#' + @id).append um.el
        $('img', um.$el).tooltip()

    addUser: (user) ->
        if not @hasUser user
            @collection.add user

    hasUser: (user) ->
        if @collection.get user.id then true else false

    removeUser: (user) ->
        @collection.remove user

    clearUser: (user) ->
        $('#' + @id + ' li:has(img[src="' + user.get("avatar") + '"])').remove()


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
        name: null
        avatar: null
        profileLink: null

    isAnonymous: ->
        not @id?

class UserList extends Backbone.Collection

    model: User

class ListView extends Backbone.View
    el: '.post-list'

    initialize: ->

        _.bindAll @

        @timeouts = {}
        @collection = new PostList
        @collection.bind 'add', @appendPost
        @collection.bind 'remove', @clearPost

    appendPost: (post) ->
        post_view = new PostView
            model: post
            id: post.eid()

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

    error: (post) ->
        @_clearTimeout post
        that = @
        $('#' + post.eid() + ' .post-resend').show().click () ->
            $('button', this).button('loading')
            $.ajax
                url: $('form').attr 'action'
                type: 'POST'
                data: post.serialize()
                error: (jqxr, status, error) =>
                    $('button', this).button 'reset'
                success: (data, status, jqxhr) =>
                    serverPost = new Post data.post
                    that.commit post, serverPost
                    $('button', this).button 'done'


    _clearTimeout: (post) ->
        clearTimeout @timeouts[post.cid]
        delete @timeouts[post.cid]

    commit: (post, serverPost) ->

        if @hasPost serverPost
            @removePost post
        @_clearTimeout post
        #$('.post-resend', '#' + post.eid()).hide()

    addTentatively: (post) ->
        console.log post
        @addPost post
        @timeouts[post.cid] = setTimeout () =>
            @error post
        , 10 * 1000

    removePost: (post) ->
        @collection.remove post

    clearPost: (post) ->
        $('#' + post.eid()).remove()

    hasPost: (post) ->
        if @collection.get post.id then true else false


class PostView extends Backbone.View
    tagName: 'li'
    className: 'post'
    template: _.template $('#post-template').html()

    initialize: ->
        _.bindAll @

    render: ->
        @$el.html @template @model.toJSON()
        if @model.isAuthor the_user
            @$el.addClass('author')
        else if @model.mentions the_user
            @$el.addClass('highlight')
        @

window.Post = class Post extends Backbone.Model

    defaults:
        message: null
        createdAtISO: (new Date()).toISOString()
        name: null
        avatar: null

    initialize: ->
        @set 'createdAtSince', Disqus.prettyDate(@get 'createdAtISO' )

    serialize: ->
        "message=" + @get 'message'

    isAuthor: (user) ->
        if the_user.isAnonymous()
            return false
        @get("name") == user.get("name")

    mentions: (user) ->
        if the_user.isAnonymous()
            return false
        @get("message").toLowerCase()
            .indexOf(user.get("name").toLowerCase()) >= 0

    eid: ->
        "post-" + @cid


class PostList extends Backbone.Collection

    model: Post


$(document).ready () ->
    window.list_view = new ListView
    window.participants_view = new ParticipantsView id: 'participant-ul'
    window.ap_view = new ParticipantsView id: 'active-ul'
    window.the_user = new User current_user

    # $('#message').keydown (e) =>
    #     if e.which == 13 and not e.shiftKey
    #         $('.new-reply form').submit()
    #         false

    $('.new-reply form').submit () ->
        if $('textarea', this).val().length <= 2
            return false

        post = new Post
            message: $('#message', this).val()
            name: the_user.get 'name'
            avatar: the_user.get 'avatar'

        list_view.addTentatively post

        $.ajax
            url: $(this).attr 'action'
            data: $(this).serialize()
            type: 'POST'
            error: (jqxhr, status, error) ->
                list_view.error(post)
            success: (data, status, jqxhr) ->
                # TODO: here just update the returned ID
                serverPost = new Post data.post
                list_view.commit post, serverPost

        $(':input', this).not(':button, :submit, :reset, :hidden').val('')

        false

    for post in initialPosts
        p = new Post(post)
        list_view.addPost(p)

    for user in initialParticipants
        p = new User user
        participants_view.addUser p

    $('.new-reply textarea').autoResize(
        maxHeight: 16
        minHeight: 82
        onAfterResize: () =>
            $('.conversation').css('padding-bottom', $('.new-reply').outerHeight())
    ).focus()

    $('.conversation').css('padding-top', $('.topic').outerHeight() + 10)

    setTimeout list_view.scrollBottom, 500


    $.getScript(realtime_host + '/socket.io/socket.io.js')
    .done (script, status) ->
        socket = io.connect realtime_host

        socket.on channels.posts, (data) ->
            payload = JSON.parse data
            p = new Post payload.data
            if payload.event == 'add'
                if not list_view.hasPost p
                    list_view.addPost p
            else
                console.log payload

        socket.on channels.participants, (data) ->
            payload = JSON.parse data
            u = new User payload.data
            console.log u
            if payload.event == 'add'
                if not participants_view.hasUser u
                    participants_view.addUser u
            else
                console.log payload

        socket.on channels.active_thread_list, (data) ->
            payload = JSON.parse data
            #u = new User payload.data
            # TODO
            console.log payload

        socket.on 'connect', () ->
            socket.emit 'connect',
                channels: _.values channels
                user: the_user.toJSON()

        socket.on 'current_peers', (peers) ->
            console.log peers
            for p in peers
                console.log p
                peer = new User p
                ap_view.addUser peer

        socket.on 'peer_disconnect', (peer) ->
            u = new User peer
            ap_view.removeUser u

        socket.on 'peer_connect', (peer) ->
            u = new User peer
            ap_view.addUser u
