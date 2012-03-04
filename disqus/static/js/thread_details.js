(function() {
  var ListView, ParticipantsView, Post, PostList, PostView, User, UserList, UserView,
    __hasProp = Object.prototype.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; };

  ParticipantsView = (function(_super) {

    __extends(ParticipantsView, _super);

    function ParticipantsView() {
      ParticipantsView.__super__.constructor.apply(this, arguments);
    }

    ParticipantsView.prototype.el = '.user-list';

    ParticipantsView.prototype.initialize = function() {
      _.bindAll(this);
      this.collection = new UserList;
      return this.collection.bind('add', this.appendUser);
    };

    ParticipantsView.prototype.appendUser = function(user) {
      var um, user_view;
      user_view = new UserView({
        model: user
      });
      um = user_view.render();
      this.$el.append(um.el);
      return $('img', um.$el).tooltip();
    };

    ParticipantsView.prototype.addUser = function(user) {
      return this.collection.add(user);
    };

    ParticipantsView.prototype.hasUser = function(user) {
      if (this.collection.get(user.id)) {
        return true;
      } else {
        return false;
      }
    };

    return ParticipantsView;

  })(Backbone.View);

  UserView = (function(_super) {

    __extends(UserView, _super);

    function UserView() {
      UserView.__super__.constructor.apply(this, arguments);
    }

    UserView.prototype.tagName = 'li';

    UserView.prototype.template = _.template($('#participant-template').html());

    UserView.prototype.initialize = function() {
      return _.bindAll(this);
    };

    UserView.prototype.render = function() {
      this.$el.html(this.template(this.model.toJSON()));
      return this;
    };

    return UserView;

  })(Backbone.View);

  window.User = User = (function(_super) {

    __extends(User, _super);

    function User() {
      User.__super__.constructor.apply(this, arguments);
    }

    User.prototype.defaults = {
      name: "matt",
      avatar: "http://mediacdn.disqus.com/uploads/users/843/7354/avatar92.jpg?1330244831",
      profileLink: "http://example.com"
    };

    return User;

  })(Backbone.Model);

  UserList = (function(_super) {

    __extends(UserList, _super);

    function UserList() {
      UserList.__super__.constructor.apply(this, arguments);
    }

    UserList.prototype.model = User;

    return UserList;

  })(Backbone.Collection);

  ListView = (function(_super) {

    __extends(ListView, _super);

    function ListView() {
      ListView.__super__.constructor.apply(this, arguments);
    }

    ListView.prototype.el = '.post-list';

    ListView.prototype.initialize = function() {
      _.bindAll(this);
      this.collection = new PostList;
      return this.collection.bind('add', this.appendPost);
    };

    ListView.prototype.appendPost = function(post) {
      var post_view;
      post_view = new PostView({
        model: post
      });
      return this.$el.append(post_view.render().el);
    };

    ListView.prototype.addPost = function(post) {
      var scrolled;
      scrolled = this.isAtBottom();
      this.collection.add(post);
      if (scrolled) return this.scrollBottom();
    };

    ListView.prototype.scrollBottom = function() {
      return $('body').animate({
        scrollTop: $(document).height()
      }, 0);
    };

    ListView.prototype.isAtBottom = function() {
      return $(window).scrollTop() + $(window).height() === $(document).height();
    };

    return ListView;

  })(Backbone.View);

  PostView = (function(_super) {

    __extends(PostView, _super);

    function PostView() {
      PostView.__super__.constructor.apply(this, arguments);
    }

    PostView.prototype.tagName = 'li';

    PostView.prototype.className = 'post';

    PostView.prototype.template = _.template($('#post-template').html());

    PostView.prototype.initialize = function() {
      return _.bindAll(this);
    };

    PostView.prototype.render = function() {
      this.$el.html(this.template(this.model.toJSON()));
      return this;
    };

    return PostView;

  })(Backbone.View);

  window.Post = Post = (function(_super) {

    __extends(Post, _super);

    function Post() {
      Post.__super__.constructor.apply(this, arguments);
    }

    Post.prototype.defaults = {
      message: 'omg',
      createdAtISO: "shrug",
      name: "matt",
      avatar: "http://mediacdn.disqus.com/uploads/users/843/7354/avatar92.jpg?1330244831"
    };

    Post.prototype.initialize = function() {
      return this.set('createdAtSince', Disqus.prettyDate(this.get('createdAtISO')));
    };

    "@make: (o) ->\n    user = new User name: o.name, avatar: o.avatar\n    delete o.name\n    delete o.avatar\n    o.user = user\n    new Post o";

    return Post;

  })(Backbone.Model);

  PostList = (function(_super) {

    __extends(PostList, _super);

    function PostList() {
      PostList.__super__.constructor.apply(this, arguments);
    }

    PostList.prototype.model = Post;

    return PostList;

  })(Backbone.Collection);

  $(document).ready(function() {
    var p, post, user, _i, _j, _len, _len2,
      _this = this;
    window.list_view = new ListView;
    window.participants_view = new ParticipantsView;
    window.the_user = new User(current_user);
    $('#message').keydown(function(e) {
      if (e.which === 13 && !e.shiftKey) {
        $('.new-reply form').submit();
        return false;
      }
    });
    $('.new-reply form').submit(function() {
      var button,
        _this = this;
      if ($('textarea', this).val().length <= 2) return false;
      button = $('button[type=submit]', this);
      if (button.attr('disabled')) return false;
      button.attr('disabled', 'disabled');
      $.ajax({
        url: $(this).attr('action'),
        data: $(this).serialize(),
        type: 'POST',
        success: function(data, status) {
          return $(':input', _this).not(':button, :submit, :reset, :hidden').val('');
        },
        complete: function(jqxhr, status) {
          return button.removeAttr('disabled');
        }
      });
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
    $('.new-reply textarea').autoResize({
      maxHeight: 84,
      minHeight: 28,
      onAfterResize: function() {
        $('.conversation').css('padding-bottom', $('.new-reply').outerHeight());
        return list_view.scrollBottom();
      }
    }).focus();
    return $.getScript(realtime_host + '/socket.io/socket.io.js').done(function(script, status) {
      var socket;
      socket = io.connect(realtime_host);
      socket.on(channels.posts, function(data) {
        var payload;
        payload = JSON.parse(data);
        p = new Post(payload.data);
        console.log(p);
        if (payload.event === 'add') {
          return list_view.addPost(p);
        } else {
          return console.log(payload);
        }
      });
      socket.on(channels.participants, function(data) {
        var payload, u;
        payload = JSON.parse(data);
        u = new User(payload.data);
        console.log(u);
        if (payload.event === 'add') {
          if (!participants_view.hasUser(u)) return participants_view.addUser(u);
        } else {
          return console.log(payload);
        }
      });
      socket.on(channels.active_thread_list, function(data) {
        var payload;
        payload = JSON.parse(data);
        return console.log(payload);
      });
      socket.on('connect', function() {
        return socket.emit('connect', {
          channels: _.values(channels),
          user: the_user.toJSON()
        });
      });
      return socket.on('peer_disconnect', function(peer) {
        var u;
        u = new User(peer);
        return console.log(u);
      });
    });
  });

}).call(this);
