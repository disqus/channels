_ = require "underscore"
connect = require 'connect'
io = require('socket.io').listen(3000)
redis = require "redis"
state = require('./lib/state.coffee')

r = redis.createClient()

substate = new state.Subscribers(r)
users = new state.Users


io.configure 'production', () ->
    io.enable 'browser client minification'
    io.enable 'browser client gzip'
    io.enable 'browser client etag'
    io.enable 'match origin protocol'

io.configure () ->
    io.set 'close timeout', 35


r.on 'message', (channel, message) ->
    _.each substate.listeners(channel), (socket) ->
        socket.emit channel, message

hello = (socket, message) ->

    for channel in _.values message.channels
        do (channel) ->
            console.log "client connected: " + socket.id
            substate.subscribe socket, channel

    postChan = message.channels.posts

    if message.user.id?
        users.register(socket, message.user)

        _.each substate.listeners(postChan), (ls) ->
            ls.emit 'peer_connect', message.user

        socket.on 'disconnect', () ->
            console.log "disconnect: " + socket.id
            # here we can actively disconnect people.

            _.each substate.peers(socket, postChan), (ps) ->
                ps.emit 'peer_disconnect', message.user
            substate.unsubscribe socket
            users.deregister socket

    socket.emit 'current_peers',
        (users.getUser ls for ls in substate.listeners postChan when users.hasUser ls)


io.sockets.on 'connection', (socket) ->
    socket.on 'hello', (message) ->
        hello socket, message


express = require "express"
require 'coffee-script'

auth = (user, pass) ->
    user == process.env.auth_user and
        pass == process.env.auth_pass

admin = express.createServer()

admin.configure () ->
    publicDir = __dirname + '/public'

    admin.use express.errorHandler dumpExceptions: true, showStack: true
    admin.use express.bodyParser()

    assets = require 'connect-assets'
    admin.use assets()

    admin.use express.static publicDir

admin.configure 'production', () ->
    admin.use connect.basicAuth(auth)


admin.get '/', (req, res) ->
    res.render 'index.jade', layout: false

admin.post '/broadcast', (req, res) ->
    message = req.body.message
    console.log "someone broadcast: " + message
    _.each users.allSockets(), (socket) ->
        socket.emit "admin_message", message
    res.send 201

admin.get '/users', (req, res) ->
    res.send users.allUsers()

admin.listen 3001
