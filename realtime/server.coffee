io = require('socket.io').listen(3000)

io.sockets.on 'connection', (socket) ->
    socket.on 'connect', (channel) ->
        socket.emit 'new_post',
            "Hello!"
        console.log channel
