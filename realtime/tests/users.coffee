state = require('../lib/state.coffee')


exports.testCrud = (test) ->

    user1 = id: 1
    user2 = id: 2
    socket1 = id: 1
    socket2 = id: 2

    f = new state.Users

    f.register(socket1, user1)
    test.ok f.hasUser socket1
    test.ok not f.hasUser socket2
    test.ok f.getUser(socket1).id == user1.id

    f.register socket2, user2
    test.ok f.allSockets().length == 2

    f.deregister socket1
    test.ok not f.hasUser socket1
    test.ok f.allSockets().length == 1

    test.done()

exports.testListUsers = (test) ->

    user1 = id: 1
    socket1 = id: 1
    socket2 = id: 2

    f = new state.Users

    f.register(socket1, user1)
    f.register(socket2, user1)

    console.log f.allUsers()
    test.ok f.allUsers().length == 1

    test.done()
