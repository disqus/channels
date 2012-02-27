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
            console.log 'subscribing'
        console.log "channel length: " + channel + ' ' +  @subscribers[channel].length

        @id2channel[socket.id] = channel

    unsubscribe: (socket) ->
        channel = @id2channel[socket.id]
        console.log "disconnect! " + channel
        @subscribers[channel] = _.filter @subscribers[channel], (member) ->
            member.id != socket.id

        if @subscribers[channel].length == 0
            console.log "unsubscribing"
            delete @subscribers[channel]
            @client.unsubscribe channel

        delete @id2channel[socket.id]
