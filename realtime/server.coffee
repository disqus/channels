_ = require "underscore"
io = require('socket.io').listen(3000)
redis = require "redis"
State = require('./lib/state.coffee').SubscriberState

r = redis.createClient()

substate = new State(r)


io.configure 'production', () ->
    io.enable 'browser client minification'
    io.enable 'browser client gzip'
    io.enable 'browser client etag'
    io.enable 'match origin protocol'

io.configure () ->
    io.set 'close timeout', 30


r.on 'message', (channel, message) ->
    _.each substate.listeners(channel), (socket) ->
        socket.emit channel,
            message

socket2user = {}

io.sockets.on 'connection', (socket) ->
    socket.on 'connect', (message) ->
        for channel in message.channels
            do (channel) ->
                console.log "client connected: " + socket.id
                substate.subscribe socket, channel
        socket2user[socket] = message.user

    socket.on 'disconnect', () ->
        # here we can actively disconnect people.
        _.each substate.peers(socket), (ps) ->
            ps.emit 'peer_disconnect', socket2user[socket]
        substate.unsubscribe socket
        console.log "client disconnected: " + socket.id
