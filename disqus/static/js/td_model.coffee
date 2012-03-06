window.User = class User extends Backbone.Model

    defaults:
        name: null
        avatar: null

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
        createdAtISO: (new Date()).toISOString()
        createdAtSince: "just now"
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
