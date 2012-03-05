window.ParticipantsView = class ParticipantsView extends Backbone.View
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
        $('#' + @id + ' li:has(img[src="' + user.get("avatar") + '"])')
            .remove()


UserView = class UserView extends Backbone.View
    tagName: 'li'
    template: _.template $('#participant-template').html()

    initialize: ->
        _.bindAll @

    render: ->
        @$el.html @template @model.toJSON()
        @


class UserList extends Backbone.Collection

    model: User


window.ActiveThreadsView = class ActiveThreadsView extends Backbone.View
    el: '#thread-list'

    initialize: ->

        _.bindAll @

        @collection = new ThreadList
        @collection.bind 'add', @appendThread
        @collection.bind 'remove', @clearThread

    appendThread: (thread) ->
        thread_view = new ThreadView model: thread

        um = thread_view.render()
        $('#' + @id).append um.el

    addThread: (thread) ->
        if not @hasThread thread
            @collection.add thread
        else
            t = @collection.get thread.id
            t.set('posts', thread.posts)

    hasThread: (thread) ->
        if @collection.get thread.id then true else false

    removethread: (thread) ->
        @collection.remove thread

    clearthread: (thread) ->
        $('li[data-thread="' + @id + '"]', el).remove()


class ThreadView extends Backbone.View
    tagName: 'li'
    className: 'thread'
    template: _.template $('#thread-template').html()

    initialize: ->
        _.bindAll @

    render: ->
        @$el.html @template @model.toJSON()
        @


class ThreadList extends Backbone.Collection

    model: Thread


window.PostListView = class PostListView extends Backbone.View
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
            $('button', this).button 'loading'
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

    addTentatively: (post) ->
        post.format()
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


class PostList extends Backbone.Collection

    model: Post
