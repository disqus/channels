State = require('./lib/state.coffee').SubscriberState


class RedisMock

    constructor: ->
        @subscribes = 0
        @unsubscribes = 0

    subscribe: (channel) ->
        @subscribes += 1

    unsubscribe: (channel) ->
        @unsubscribes += 1

exports.testSomething = (test) ->
    mock = new RedisMock()
    s = new State mock
    channel = 'testchannel'
    s.subscribe id: 1234, channel
    s.subscribe id: 4321, channel

    test.ok s.subscribers[channel].length == 2
    test.ok mock.subscribes = 1

    s.unsubscribe id: 1234

    test.ok s.subscribers[channel].length == 1, "length"
    test.ok mock.subscribes == 1, "subscribes"
    test.ok mock.unsubscribes == 0, "unsubscribes"

    test.done()
