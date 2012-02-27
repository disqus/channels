io = require('socket.io').listen(80)

io.sockets.on 'connection', (socket) ->
  socket.on('connect', (channel) ->
    console.log channel
