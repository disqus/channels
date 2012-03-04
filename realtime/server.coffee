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

        if message.user.id?
            socket2user[socket.id] = message.user

            _.each substate.peers(socket), (ps) ->
                ps.emit 'peer_connect', socket2user[socket.id]

        console.log message.user
        ids = (ps.id for ps in substate.peers socket)
        ids.push socket.id
        console.log ids
        console.log socket2user
        socket.emit 'current_peers',
            (socket2user[id] for id in _.unique ids when socket2user[id]?)


    socket.on 'disconnect', () ->
        console.log "disconnect: " + socket.id
        # here we can actively disconnect people.
        _.each substate.peers(socket), (ps) ->
            ps.emit 'peer_disconnect', socket2user[socket.id]
        substate.unsubscribe socket
        delete socket2user[socket.id]
