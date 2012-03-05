window.User = class User extends Backbone.Model

    defaults:
        name: null
        avatar: null

    isAnonymous: ->
        not @id?

window.Thread = class Thread extends Backbone.Model

    defaults:
        title: null
        posts: null

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

    format: ->
        new_text = "<p>" + @get("message").replace(/\n\n/g, "</p><p>").replace(/\n/g, "<br/>") + "</p>"
        @set "message", new_text

    eid: ->
        "post-" + @cid