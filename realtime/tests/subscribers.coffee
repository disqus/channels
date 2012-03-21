state = require('../lib/state.coffee')
_ = require "underscore"


class RedisMock

    constructor: ->
        @subscribes = 0
        @unsubscribes = 0

    subscribe: (channel) ->
        @subscribes += 1

    unsubscribe: (channel) ->
        @unsubscribes += 1

exports.testSubscribe = (test) ->
    mock = new RedisMock()
    s = new state.Subscribers mock
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

exports.testMultipleChannels = (test) ->
    mock = new RedisMock()
    s = new state.Subscribers mock
    channel1 = 'testchannel'
    channel2 = 'testchannel2'
    s.subscribe id: 1234, channel1
    s.subscribe id: 1234, channel2

    test.ok s.id2channel[1234].length == 2
    test.ok s.subscribers[channel1].length == 1
    test.ok s.subscribers[channel2].length == 1
    test.ok mock.subscribes = 2

    s.unsubscribe id: 1234

    test.ok s.subscribers[channel1] == undefined
    test.ok s.subscribers[channel2] == undefined
    test.ok mock.subscribes == 2, "sanity check that we subscribe twice"
    test.ok mock.unsubscribes == 2, "Test that we don't unsubscribe yet"

    test.done()

exports.testPeers = (test) ->
    mock = new RedisMock()
    s = new state.Subscribers mock
    channel1 = 'testchannel'
    channel2 = 'testchannel2'
    channel3 = 'testchannel3'
    s.subscribe id: 123, channel1
    s.subscribe id: 123, channel2
    s.subscribe id: 456, channel2
    s.subscribe id: 456, channel3
    s.subscribe id: 789, channel3

    res = s.peers id: 123
    test.ok res.length == 2

    test.done()

exports.testListeners = (test) ->
    mock = new RedisMock()
    s = new state.Subscribers mock
    channel1 = 'testchannel'
    channel2 = 'testchannel2'
    channel3 = 'testchannel3'
    channel4 = 'testchannel4'
    s.subscribe id: 123, channel1
    s.subscribe id: 123, channel2
    s.subscribe id: 123, channel4
    s.subscribe id: 456, channel2
    s.subscribe id: 456, channel4
    s.subscribe id: 456, channel3

    test.ok s.listeners(channel1).length == 1, "[id: 123]"
    test.ok s.listeners(channel2).length == 2, "[id: 123, id: 456]"
    test.ok s.listeners(channel3).length == 1, "[id: 456]"

    test.done()
