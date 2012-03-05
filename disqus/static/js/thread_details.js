(function() {

  $(document).ready(function() {
    var p, post, thread, user, _i, _j, _k, _l, _len, _len2, _len3, _len4,
      _this = this;
    window.list_view = new PostListView;
    window.participants_view = new ParticipantsView({
      id: 'participant_list'
    });
    window.ap_view = new ParticipantsView({
      id: 'active_participant_list'
    });
    window.the_user = new User(current_user);
    window.threads_view = new ActiveThreadsView({
      id: 'thread_list'
    });
    window.my_threads_view = new ActiveThreadsView({
      id: 'my_thread_list'
    });
    $('#message').keydown(function(e) {
      if (e.which === 13 && e.shiftKey) {
        $('.new-reply form').submit();
        return false;
      }
    });
    $('.new-reply form').submit(function() {
      var post;
      if ($('textarea', this).val().length <= 2) return false;
      post = new Post({
        message: $('#message', this).val(),
        name: the_user.get('name'),
        avatar: the_user.get('avatar')
      });
      list_view.addTentatively(post);
      $.ajax({
        url: $(this).attr('action'),
        data: $(this).serialize(),
        type: 'POST',
        error: function(jqxhr, status, error) {
          return list_view.error(post);
        },
        success: function(data, status, jqxhr) {
          var serverPost;
          serverPost = new Post(data.post);
          return list_view.commit(post, serverPost);
        }
      });
      $(':input', this).not(':button, :submit, :reset, :hidden').val('');
      return false;
    });
    for (_i = 0, _len = initialPosts.length; _i < _len; _i++) {
      post = initialPosts[_i];
      p = new Post(post);
      list_view.addPost(p);
    }
    for (_j = 0, _len2 = initialParticipants.length; _j < _len2; _j++) {
      user = initialParticipants[_j];
      p = new User(user);
      participants_view.addUser(p);
    }
    for (_k = 0, _len3 = initialThreads.length; _k < _len3; _k++) {
      thread = initialThreads[_k];
      p = new Thread(thread);
      threads_view.addThread(p);
    }
    for (_l = 0, _len4 = initialMyThreads.length; _l < _len4; _l++) {
      thread = initialMyThreads[_l];
      p = new Thread(thread);
      my_threads_view.addThread(p);
    }
    $('.new-reply textarea').autoResize({
      maxHeight: 82,
      minHeight: 82,
      onAfterResize: function() {
        return $('.conversation').css('padding-bottom', $('.new-reply').outerHeight());
      }
    }).focus();
    $('.conversation').css('padding-top', $('.topic').outerHeight() + 10);
    setTimeout(list_view.scrollBottom, 500);
    return $.getScript(realtime_host + '/socket.io/socket.io.js').done(function(script, status) {
      var socket;
      socket = io.connect(realtime_host);
      socket.on(channels.posts, function(data) {
        var payload;
        payload = JSON.parse(data);
        p = new Post(payload.data);
        if (payload.event === 'add') {
          if (!list_view.hasPost(p)) return list_view.addPost(p);
        } else {
          return console.log(payload);
        }
      });
      socket.on(channels.participants, function(data) {
        var payload, u;
        payload = JSON.parse(data);
        u = new User(payload.data);
        if (payload.event === 'add') {
          return participants_view.addUser(u);
        } else {
          return console.log(payload);
        }
      });
      socket.on(channels.active_thread_list, function(data) {
        var payload, t;
        payload = JSON.parse(data);
        t = new Thread(payload.data);
        if (payload.event === 'add') {
          return threads_view.addThread(t);
        } else {
          return console.log(payload);
        }
      });
      socket.on(channels.my_thread_list, function(data) {
        var payload, t;
        payload = JSON.parse(data);
        t = new Thread(payload.data);
        if (payload.event === 'add') {
          return my_threads_view.addThread(t);
        } else {
          return console.log(payload);
        }
      });
      socket.on('connect', function() {
        return socket.emit('connect', {
          channels: _.values(channels),
          user: the_user.toJSON()
        });
      });
      socket.on('current_peers', function(peers) {
        var p, peer, _len5, _m, _results;
        console.log(peers);
        _results = [];
        for (_m = 0, _len5 = peers.length; _m < _len5; _m++) {
          p = peers[_m];
          console.log(p);
          peer = new User(p);
          _results.push(ap_view.addUser(peer));
        }
        return _results;
      });
      socket.on('peer_disconnect', function(peer) {
        var u;
        u = new User(peer);
        return ap_view.removeUser(u);
      });
      return socket.on('peer_connect', function(peer) {
        var u;
        u = new User(peer);
        return ap_view.addUser(u);
      });
    });
  });

}).call(this);
