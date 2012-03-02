(function() {
  var ListView, Post, PostList, PostView,
    __hasProp = Object.prototype.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; };

  ListView = (function(_super) {

    __extends(ListView, _super);

    function ListView() {
      ListView.__super__.constructor.apply(this, arguments);
    }

    ListView.prototype.el = '.post-list';

    ListView.prototype.initialize = function() {
      _.bindAll(this);
      this.collection = new PostList;
      this.collection.bind('add', this.appendPost);
      return this.render();
    };

    ListView.prototype.render = function() {
      return this.$el.append('<ul class="post-list"></ul>');
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
    var p, post, _i, _len,
      _this = this;
    window.list_view = new ListView;
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
      socket.on('new_post', function(post) {
        p = new Post(JSON.parse(post));
        console.log(p);
        return list_view.addPost(p);
      });
      return socket.on('connect', function() {
        return socket.emit('connect', {
          channel: channels.posts
        });
      });
    });
  });

}).call(this);
