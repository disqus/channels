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
      this.collection.bind('add', this.appendUser);
      return this.collection.bind('remove', this.clearUser);
    };

    ParticipantsView.prototype.appendUser = function(user) {
      var um, user_view;
      user_view = new UserView({
        model: user
      });
      um = user_view.render();
      $('#' + this.id).append(um.el);
      return $('img', um.$el).tooltip();
    };

    ParticipantsView.prototype.addUser = function(user) {
      if (!this.hasUser(user)) return this.collection.add(user);
    };

    ParticipantsView.prototype.hasUser = function(user) {
      if (this.collection.get(user.id)) {
        return true;
      } else {
        return false;
      }
    };

    ParticipantsView.prototype.removeUser = function(user) {
      return this.collection.remove(user);
    };

    ParticipantsView.prototype.clearUser = function(user) {
      return $('#' + this.id + ' li:has(img[src="' + user.get("avatar") + '"])').remove();
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
      name: null,
      avatar: null,
      profileLink: null
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
      this.timeouts = {};
      this.collection = new PostList;
      return this.collection.bind('add', this.appendPost);
    };

    ListView.prototype.appendPost = function(post) {
      var post_view;
      post_view = new PostView({
        model: post,
        id: post.eid()
      });
      this.$el.append(post_view.render().el);
      if (post.get("message").indexOf(the_user.get("name")) >= 0) {
        return post_view.$el.addClass('alert alert-info');
      }
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

    ListView.prototype.error = function(post) {
      var that;
      this._clearTimeout(post);
      that = this;
      return $('#' + post.eid() + ' .post-resend').show().click(function() {
        var _this = this;
        $('button', this).button('loading');
        return $.ajax({
          url: $('form').attr('action'),
          type: 'POST',
          data: post.serialize(),
          error: function(jqxr, status, error) {
            return $('button', _this).button('reset');
          },
          success: function(jqxr, status) {
            that.commit(post);
            return $('button', _this).button('done');
          }
        });
      });
    };

    ListView.prototype._clearTimeout = function(post) {
      clearTimeout(this.timeouts[post.cid]);
      return delete this.timeouts[post.cid];
    };

    ListView.prototype.commit = function(post) {
      this._clearTimeout(post);
      return $('.post-resend', '#' + post.eid()).hide();
    };

    ListView.prototype.addTentatively = function(post) {
      var _this = this;
      console.log(post);
      this.addPost(post);
      return this.timeouts[post.cid] = setTimeout(function() {
        return _this.error(post);
      }, 10 * 1000);
    };

    ListView.prototype.removePlaceholder = function(post) {
      var placeholder;
      placeholder = this.collection.find(function(p) {
        return p.get("name") === post.get("name") && !(p.id != null);
      });
      return $('#' + placeholder.eid()).remove();
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
      message: null,
      createdAtISO: (new Date()).toISOString(),
      name: null,
      avatar: null
    };

    Post.prototype.initialize = function() {
      return this.set('createdAtSince', Disqus.prettyDate(this.get('createdAtISO')));
    };

    Post.prototype.serialize = function() {
      return "message=" + this.get('message');
    };

    Post.prototype.eid = function() {
      return "post-" + this.cid;
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
    window.participants_view = new ParticipantsView({
      id: 'participant-ul'
    });
    window.ap_view = new ParticipantsView({
      id: 'active-ul'
    });
    window.the_user = new User(current_user);
    $('#message').keydown(function(e) {
      if (e.which === 13 && !e.shiftKey) {
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
        success: function(jqxr, status) {
          return list_view.commit(post);
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
    $('.new-reply textarea').autoResize({
      maxHeight: 84,
      minHeight: 28,
      onAfterResize: function() {
        $('.conversation').css('padding-bottom', $('.new-reply').outerHeight());
        return setTimeout(list_view.scrollBottom, 500);
      }
    }).focus();
    return $.getScript(realtime_host + '/socket.io/socket.io.js').done(function(script, status) {
      var socket;
      socket = io.connect(realtime_host);
      socket.on(channels.posts, function(data) {
        var payload;
        payload = JSON.parse(data);
        p = new Post(payload.data);
        if (payload.event === 'add') {
          if (p.get("name") === the_user.get("name")) {
            list_view.removePlaceholder(p);
          }
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
      socket.on('current_peers', function(peers) {
        var p, peer, _k, _len3, _results;
        console.log(peers);
        _results = [];
        for (_k = 0, _len3 = peers.length; _k < _len3; _k++) {
          p = peers[_k];
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
