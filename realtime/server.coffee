_ = require "underscore"
io = require('socket.io').listen(3000)
redis = require "redis"
State = require('./lib/state.coffee').SubscriberState

client = redis.createClient()

substate = new State(client)


client.on 'message', (channel, message) ->
    console.log "new message: " + message
    _.each substate.channel2socket(channel), (socket) ->
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
        substate.subscribe socket, channel

    socket.on 'disconnect', () ->
        substate.unsubscribe socket
