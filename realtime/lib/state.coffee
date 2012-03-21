_ = require "underscore"


exports.Subscribers = class

    constructor: (@client) ->
        @subscribers = {}
        @id2channel = {}

    subscribe: (socket, channel) ->

        if _.has @subscribers, channel
            @subscribers[channel].push socket
        else
            @subscribers[channel] = [socket]
            @client.subscribe channel
            console.log "subscribing to channel: " + channel
        console.log "channel length: " + channel + ' ' +  @subscribers[channel].length

        if _.has @id2channel, socket.id
            @id2channel[socket.id].push channel
        else
            @id2channel[socket.id] = [channel]

    unsubscribe: (socket) ->
        channels = @id2channel[socket.id]
        return if not channels?
        filter = (member) ->
            member.id != socket.id

        for channel of @subscribers
            @subscribers[channel] = _.filter @subscribers[channel], (member) ->
                member.id != socket.id

            if @subscribers[channel].length == 0
                console.log "unsubscribing from channel: " + channel
                delete @subscribers[channel]
                @client.unsubscribe channel

        delete @id2channel[socket.id]

    listeners: (channel) ->
        @subscribers[channel]

    peers: (socket, channel) ->
        p = []
        for channel in @id2channel[socket.id]
            if _.isUndefined @listeners channel
                continue
            cp = _.filter @listeners(channel), (s) ->
                s.id != socket.id
            if cp.length > 0
                p.push cp
        p.push socket
        _.unique _.flatten p


exports.Users = class

    constructor: () ->
        @sid2user = {}
        @sid2socket = {}

    register: (socket, user) ->
        @sid2user[socket.id] = user
        @sid2socket[socket.id] = socket

    getUser: (socket) ->
        @sid2user[socket.id]

    hasUser: (socket) ->
        @sid2user[socket.id]?

    deregister: (socket) ->
        delete @sid2user[socket.id]
        delete @sid2socket[socket.id]

    allSockets: () ->
        _.values @sid2socket

    allUsers: () ->
        _.unique _.values @sid2user
