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

    test.ok s.subscribers[channel].length == 1, "One connection left"
    test.ok mock.subscribes == 1, "sanity check that we subscribe once only"
    test.ok mock.unsubscribes == 0, "Test that we don't unsubscribe yet"

    s.unsubscribe id: 4321
    test.ok s.subscribers[channel] == undefined, "no connections"
    test.ok mock.unsubscribes == 1,
        "Test that we unsubscribe when last user parts"

    test.done()