_ = require "underscore"
io = require('socket.io').listen(3000)
redis = require "redis"

client = redis.createClient()

subscribers = {}
id2channel = {}

client.on 'message', (channel, message) ->
    console.log "new message: " + message
    _.each subscribers[channel], (socket) ->
        socket.emit 'new_post',
            message

"""
client.on 'unsubscribe', (channel) ->
    delete subscribers[channel]
"""



io.sockets.on 'connection', (socket) ->
    socket.on 'connect', (message) ->
        channel = message.channel
        console.log channel

        if _.has subscribers, channel and _.size(subscribers[channel]) > 0
            subscribers[channel].push socket
        else
            subscribers[channel] = [socket]
            client.subscribe channel
            console.log 'subscribing'
        console.log "channel length: " + channel + ' ' +  subscribers[channel].length

        id2channel[socket.id] = channel

    socket.on 'disconnect', () ->
        console.log "disconnect!"
        channel = id2channel[socket.id]
        subscribers[channel] = _.without subscribers[channel], socket
        if subscribers[channel].length == 0
            console.log "unsubscribing"
            delete subscribers[channel]
            client.unsubscribe channel
        delete id2channel[socket.id]
