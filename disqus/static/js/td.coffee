class Autocomplete

    constructor: (@source_cb) ->
        @lastMatch = null
        @matches = null
        @i = null

    _next: ->
        if @i == @matches.length
            @i = 0
        @matches[@i++]

    next: (text) ->
        if text != @lastMatch
            @i = 0
            @matches = _.filter @source_cb(), (name) =>
                name.toLowerCase().indexOf(text.toLowerCase()) == 0

        return @lastMatch = @_next()


$(document).ready () ->
    window.the_user = new User current_user
    window.list_view = new PostListView
    window.participants_view = new ParticipantsView id: 'participant_list'
    window.ap_view = new ParticipantsView id: 'active_participant_list'
    window.threads_view = new ActiveThreadsView id: 'thread_list'
    window.my_threads_view = new ActiveThreadsView id: 'my_thread_list'
    window.player = $('#dplayer embed')[0]


    ac = new Autocomplete participants_view.usernameList

    $('#message').keydown (e) ->
        if e.which == 13 and e.shiftKey
            $('.new-reply form').submit()
            return false

        if e.which == 9 and $(this).val().indexOf(' ') < 0
            match = ac.next $(this).val()
            if match?
                $(this).val(match)

            return false

    $('.new-reply form').submit () ->

        post = new Post
            message: $('textarea', this).val()
            name: the_user.get 'name'
            avatar: the_user.get 'avatar'

        if not post.isValid()
            return false

        list_view.addTentatively post

        $.ajax
            url: $(this).attr 'action'
            data: $(this).serialize()
            type: 'POST'
            error: (jqxhr, status, error) ->
                list_view.error(post)
            success: (data, status, jqxhr) ->
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

    for thread in initialThreads
        p = new Thread thread
        threads_view.addThread p

    for thread in initialMyThreads
        p = new Thread thread
        my_threads_view.addThread p

    $('.new-reply textarea').autoResize(
        maxHeight: 82
        minHeight: 82
        onAfterResize: () =>
            $('.conversation').css 'padding-bottom',
                $('.new-reply').outerHeight()
    ).focus()

    $('.conversation').css('padding-top', $('.topic').outerHeight() + 10)

    setTimeout list_view.scrollBottom, 500


    $.getScript(realtime_host + '/socket.io/socket.io.js')
    .done (script, status) ->
        socket = io.connect realtime_host

        socket.on 'connect', () ->
            socket.emit 'hello',
                channels: channels
                user: the_user.toJSON()

        socket.on channels.posts, (data) ->
            payload = JSON.parse data
            p = new Post payload.data
            if payload.event == 'add'
                if not p.isAuthor(the_user)
                    list_view.addPost p
            else
                console.log payload

        socket.on channels.participants, (data) ->
            payload = JSON.parse data
            u = new User payload.data
            if payload.event == 'add'
                participants_view.addUser u
            else
                console.log payload

        socket.on channels.active_thread_list, (data) ->
            payload = JSON.parse data
            t = new Thread payload.data
            if payload.event == 'add'
                threads_view.addThread t
            else
                console.log payload

        socket.on channels.my_thread_list, (data) ->
            payload = JSON.parse data
            t = new Thread payload.data
            if payload.event == 'add'
                my_threads_view.addThread t
            else
                console.log payload

        socket.on 'current_peers', (peers) ->
            for p in peers
                peer = new User p
                ap_view.addUser peer

        socket.on 'peer_disconnect', (peer) ->
            u = new User peer
            ap_view.removeUser u

        socket.on 'peer_connect', (peer) ->
            u = new User peer
            ap_view.addUser u

