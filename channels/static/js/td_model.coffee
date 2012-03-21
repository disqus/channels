window.User = class User extends Backbone.Model

    defaults:
        name: null
        avatar: null
        hash: "8c6e68c5cf4694cb13f4f51575885b21"

    isAnonymous: ->
        not @id?

    isUser: (user) ->
        @id == user.id

window.Thread = class Thread extends Backbone.Model

    defaults:
        title: null
        posts: null

window.Post = class Post extends Backbone.Model

    defaults:
        message: null
        # TODO: make this update
        createdAtISO: null
        createdAtSince: "just now"
        name: null
        avatar: null
        hash: "8c6e68c5cf4694cb13f4f51575885b21"
        class: 'user'

    initialize: ->
        if not @get 'createdAtISO'
            @set 'createdAtISO', (new Date()).toISOString()
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

    formattedMsg: ->
        "<p>" + @get("message")
            .replace(/\n\n/g, "</p><p>")
            .replace(/\n/g, "<br/>") + "</p>"

    eid: ->
        "post-" + @cid

    validate: ->
        msg = @get "message"
        if msg.replace(/\s/g, '').length < 3
            return "Message too short"
        if msg.split(/\s/g).length - 1 is msg.length
            return "Will not accept blank message."
