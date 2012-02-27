io = require('socket.io').listen(3000)
redis = require "redis"

client = redis.createClient()

subscribers = {}

client.on 'message', (channel, message) ->
    socket = subscribers[channel]
    socket.emit 'new_post',
        message

client.on 'unsubscribe', (channel) ->
    false

io.sockets.on 'connection', (socket) ->
    socket.on 'connect', (message) ->
        channel = message.channel
        console.log channel
        subscribers[channel] = socket
        client.subscribe channel
        client.emit 'new_post', "post"
