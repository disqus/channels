_ = require "underscore"


exports.SubscriberState = class

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

    peers: (socket) ->
        peers = []
        for channel in @id2channel[socket.id]
            cp = _.filter @listeners(channel), (s) ->
                s.id != socket.id
            if cp.length > 0
                peers.push cp
        _.unique _.flatten peers
