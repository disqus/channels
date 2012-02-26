(function() {
  var Details, Post, PostList, PostView,
    __hasProp = Object.prototype.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; };

  Details = (function() {

    function Details() {
      var _this = this;
      this.scrollBottom();
      $('.new-reply textarea').autoResize({
        maxHeight: 84,
        minHeight: 28,
        onAfterResize: function() {
          $('.conversation-stream').css('padding-bottom', $('.new-reply').height() + 10);
          return _this.scrollBottom();
        }
      }).focus();
      $('#message').keydown(function(e) {
        if (e.which === 13 && !e.shiftKey) {
          $('.new-reply form').submit();
          return false;
        }
      });
      $('.new-reply form').submit(function() {
        var button,
          _this = this;
        button = $('button[type=submit]', this);
        setTimeout(function() {
          return button.attr('disabled', 'disabled');
        }, 50);
        if (button.attr('disabled')) return false;
      });
    }

    Details.prototype.scrollBottom = function() {
      return $('body').animate({
        scrollTop: $(document).height()
      }, 0);
    };

    return Details;

  })();

  PostView = (function(_super) {

    __extends(PostView, _super);

    function PostView() {
      PostView.__super__.constructor.apply(this, arguments);
    }

    PostView.prototype.el = $('.conversation-stream');

    PostView.prototype.initialize = function() {
      _.bindAll(this);
      this.collection = new PostList;
      this.collection.bind('add', this.appendPost);
      return this.render();
    };

    PostView.prototype.render = function() {
      return $(this.el).append('<ul class="post-list"></ul>');
    };

    PostView.prototype.appendPost = function() {
      return $('.post-list').append("<li>Hi!</li>");
    };

    PostView.prototype.addPost = function() {
      var post;
      post = new Post;
      return this.collection.add(post);
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
    window.postView = new PostView;
    return new Details();
  });

}).call(this);
