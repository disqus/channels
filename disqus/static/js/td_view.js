(function() {
  var ActiveThreadsView, ParticipantsView, PostList, PostListView, PostView, ThreadList, ThreadView, UserList, UserView,
    __hasProp = Object.prototype.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; };

  window.ParticipantsView = ParticipantsView = (function(_super) {

    __extends(ParticipantsView, _super);

    function ParticipantsView() {
      ParticipantsView.__super__.constructor.apply(this, arguments);
    }

    ParticipantsView.prototype.el = '.user-list';

    ParticipantsView.prototype.initialize = function() {
      _.bindAll(this);
      this.collection = new UserList;
      this.collection.on('add', this.appendUser);
      this.collection.on('remove', this.clearUser);
      this.collection.on('add remove', this.changed);
      return this.addUser(window.the_user);
    };

    ParticipantsView.prototype.changed = function() {
      return this.trigger("membership");
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
      if (!this.hasUser(user) && !user.isAnonymous()) {
        return this.collection.add(user);
      }
    };

    ParticipantsView.prototype.hasUser = function(user) {
      if (this.collection.get(user.id)) {
        return true;
      } else {
        return false;
      }
    };

    ParticipantsView.prototype.removeUser = function(user) {
      if (!user.isUser(window.the_user)) return this.collection.remove(user);
    };

    ParticipantsView.prototype.clearUser = function(user) {
      return $('#' + this.id + ' li:has(img[src="' + user.get("avatar") + '"])').remove();
    };

    ParticipantsView.prototype.usernameList = function() {
      return this.collection.map(function(user) {
        return user.get("name");
      });
    };

    ParticipantsView.prototype.addTestData = function() {
      var _this = this;
      return _.each(['matt', 'maybe', 'mell', 'martha'], function(n) {
        return _this.addUser(new User({
          name: n,
          id: n + '1',
          avatar: 'https://securecdn.disqus.com/uploads/users/843/7354/avatar92.jpg?1330749766'
        }));
      });
    };

    return ParticipantsView;

  })(Backbone.View);

  UserView = UserView = (function(_super) {

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

  UserList = (function(_super) {

    __extends(UserList, _super);

    function UserList() {
      UserList.__super__.constructor.apply(this, arguments);
    }

    UserList.prototype.model = User;

    return UserList;

  })(Backbone.Collection);

  window.ActiveThreadsView = ActiveThreadsView = (function(_super) {

    __extends(ActiveThreadsView, _super);

    function ActiveThreadsView() {
      ActiveThreadsView.__super__.constructor.apply(this, arguments);
    }

    ActiveThreadsView.prototype.el = '#thread-list';

    ActiveThreadsView.prototype.initialize = function() {
      _.bindAll(this);
      this.collection = new ThreadList;
      this.collection.on('add', this.appendThread);
      return this.collection.on('remove', this.clearThread);
    };

    ActiveThreadsView.prototype.appendThread = function(thread) {
      var thread_view, um;
      thread_view = new ThreadView({
        model: thread,
        id: this.id + thread.id
      });
      um = thread_view.render();
      return $('#' + this.id).append(um.el);
    };

    ActiveThreadsView.prototype.addThread = function(thread) {
      var t;
      if (!this.hasThread(thread)) {
        return this.collection.add(thread);
      } else {
        t = this.collection.get(thread.id);
        return t.set('posts', thread.get("posts"));
      }
    };

    ActiveThreadsView.prototype.hasThread = function(thread) {
      if (this.collection.get(thread.id)) {
        return true;
      } else {
        return false;
      }
    };

    ActiveThreadsView.prototype.removethread = function(thread) {
      return this.collection.remove(thread);
    };

    ActiveThreadsView.prototype.clearthread = function(thread) {
      return $('li[data-thread="' + this.id + '"]', el).remove();
    };

    return ActiveThreadsView;

  })(Backbone.View);

  ThreadView = (function(_super) {

    __extends(ThreadView, _super);

    function ThreadView() {
      ThreadView.__super__.constructor.apply(this, arguments);
    }

    ThreadView.prototype.tagName = 'li';

    ThreadView.prototype.className = 'thread';

    ThreadView.prototype.template = _.template($('#thread-template').html());

    ThreadView.prototype.initialize = function() {
      _.bindAll(this);
      return this.model.on("change:posts", this.updatePosts);
    };

    ThreadView.prototype.updatePosts = function(p) {
      return $('.thread-count', this.$el).text(this.model.get("posts"));
    };

    ThreadView.prototype.render = function() {
      this.$el.html(this.template(this.model.toJSON()));
      return this;
    };

    return ThreadView;

  })(Backbone.View);

  ThreadList = (function(_super) {

    __extends(ThreadList, _super);

    function ThreadList() {
      ThreadList.__super__.constructor.apply(this, arguments);
    }

    ThreadList.prototype.model = Thread;

    return ThreadList;

  })(Backbone.Collection);

  window.PostListView = PostListView = (function(_super) {

    __extends(PostListView, _super);

    function PostListView() {
      PostListView.__super__.constructor.apply(this, arguments);
    }

    PostListView.prototype.el = '.post-list';

    PostListView.prototype.initialize = function() {
      _.bindAll(this);
      this.timeouts = {};
      this.collection = new PostList;
      this.collection.on('add', this.appendPost);
      return this.collection.on('remove', this.clearPost);
    };

    PostListView.prototype.appendPost = function(post) {
      var post_view, scrolled;
      post_view = new PostView({
        model: post,
        id: post.eid()
      });
      scrolled = this.isAtBottom();
      this.$el.append(post_view.render(post.isNew()).el);
      if (scrolled) return this.scrollBottom();
    };

    PostListView.prototype.addPost = function(post) {
      return this.collection.add(post);
    };

    PostListView.prototype.scrollBottom = function() {
      return $('body').animate({
        scrollTop: $(document).height()
      }, 0);
    };

    PostListView.prototype.isAtBottom = function() {
      return $(window).scrollTop() + $(window).height() === $(document).height();
    };

    PostListView.prototype.error = function(post) {
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
          success: function(data, status, jqxhr) {
            var serverPost;
            serverPost = new Post(data.post);
            that.commit(post, serverPost);
            return $('button', _this).button('done');
          }
        });
      });
    };

    PostListView.prototype._clearTimeout = function(post) {
      clearTimeout(this.timeouts[post.cid]);
      return delete this.timeouts[post.cid];
    };

    PostListView.prototype.commit = function(post, serverPost) {
      var scrolled;
      scrolled = this.isAtBottom();
      post.set("message", serverPost.get("message"));
      if (scrolled) this.scrollBottom();
      post.id = serverPost.id;
      return this._clearTimeout(post);
    };

    PostListView.prototype.addTentatively = function(post) {
      var _this = this;
      this.addPost(post);
      return this.timeouts[post.cid] = setTimeout(function() {
        return _this.error(post);
      }, 10 * 1000);
    };

    PostListView.prototype.removePost = function(post) {
      return this.collection.remove(post);
    };

    PostListView.prototype.clearPost = function(post) {
      return $('#' + post.eid()).remove();
    };

    PostListView.prototype.hasPost = function(post) {
      if (this.collection.get(post.id)) {
        return true;
      } else {
        return false;
      }
    };

    return PostListView;

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
      _.bindAll(this);
      return this.model.on('change:message', this.updateMessage);
    };

    PostView.prototype.updateMessage = function(post) {
      return $('#' + this.model.eid() + ' .post-message').html(this.model.get("message"));
    };

    PostView.prototype.render = function(format) {
      var obj;
      obj = this.model.toJSON();
      if (format != null) obj.message = this.model.formattedMsg();
      this.$el.html(this.template(obj));
      if (this.model.isAuthor(window.the_user)) {
        this.$el.addClass('author');
      } else if (this.model.mentions(window.the_user)) {
        if ((typeof ding !== "undefined" && ding !== null) && (ding.play != null)) {
          ding.play;
        }
        this.$el.addClass('highlight');
      }
      return this;
    };

    return PostView;

  })(Backbone.View);

  PostList = (function(_super) {

    __extends(PostList, _super);

    function PostList() {
      PostList.__super__.constructor.apply(this, arguments);
    }

    PostList.prototype.model = Post;

    return PostList;

  })(Backbone.Collection);

}).call(this);
