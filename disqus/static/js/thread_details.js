(function() {
  var Details, ListView, Post, PostList, PostView,
    __hasProp = Object.prototype.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; };

  Details = (function() {

    function Details() {}

    return Details;

  })();

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
      this.render();
      return this.scrollBottom();
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

    ListView.prototype.addPost = function() {
      var post;
      post = new Post;
      this.collection.add(post);
      return this.scrollBottom();
    };

    ListView.prototype.scrollBottom = function() {
      return $('body').animate({
        scrollTop: $(document).height()
      }, 0);
    };

    return ListView;

  })(Backbone.View);

  PostView = (function(_super) {

    __extends(PostView, _super);

    function PostView() {
      PostView.__super__.constructor.apply(this, arguments);
    }

    PostView.prototype.tagName = 'li';

    PostView.prototype.initialize = function() {
      return _.bindAll(this);
    };

    PostView.prototype.render = function() {
      this.$el.html('<li>HI!</li>');
      return this;
    };

    return PostView;

  })(Backbone.View);

  Post = (function(_super) {

    __extends(Post, _super);

    function Post() {
      Post.__super__.constructor.apply(this, arguments);
    }

    Post.prototype.defaults = {
      message: 'omg'
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
    var _this = this;
    window.list_view = new ListView;
    $('.new-reply textarea').autoResize({
      maxHeight: 84,
      minHeight: 28,
      onAfterResize: function() {
        $('.conversation-stream').css('padding-bottom', $('.new-reply').height() + 10);
        return list_view.scrollBottom();
      }
    }).focus();
    $('#message').keydown(function(e) {
      if (e.which === 13 && !e.shiftKey) {
        $('.new-reply form').submit();
        return false;
      }
    });
    return $('.new-reply form').submit(function() {
      var button,
        _this = this;
      button = $('button[type=submit]', this);
      setTimeout(function() {
        return button.attr('disabled', 'disabled');
      }, 50);
      if (button.attr('disabled')) return false;
    });
  });

}).call(this);
