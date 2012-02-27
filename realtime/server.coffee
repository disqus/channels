io = require('socket.io').listen(3000)
redis = require "redis"
State = require('./lib/state.coffee').SubscriberState

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

substate = new State(client)


io.sockets.on 'connection', (socket) ->
    socket.on 'connect', (message) ->
        channel = message.channel
        console.log channel
        substate.subscribe socket, channel

    socket.on 'disconnect', () ->
        substate.unsubscribe socket
