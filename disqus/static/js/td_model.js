(function() {
  var Post, Thread, User,
    __hasProp = Object.prototype.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; };

  window.User = User = (function(_super) {

    __extends(User, _super);

    function User() {
      User.__super__.constructor.apply(this, arguments);
    }

    User.prototype.defaults = {
      name: null,
      avatar: null
    };

    User.prototype.isAnonymous = function() {
      return !(this.id != null);
    };

    User.prototype.isUser = function(user) {
      return this.id === user.id;
    };

    return User;

  })(Backbone.Model);

  window.Thread = Thread = (function(_super) {

    __extends(Thread, _super);

    function Thread() {
      Thread.__super__.constructor.apply(this, arguments);
    }

    Thread.prototype.defaults = {
      title: null,
      posts: null
    };

    return Thread;

  })(Backbone.Model);

  window.Post = Post = (function(_super) {

    __extends(Post, _super);

    function Post() {
      Post.__super__.constructor.apply(this, arguments);
    }

    Post.prototype.defaults = {
      message: null,
      createdAtISO: (new Date()).toISOString(),
      createdAtSince: "just now",
      name: null,
      avatar: null
    };

    Post.prototype.initialize = function() {
      return this.set('createdAtSince', Disqus.prettyDate(this.get('createdAtISO')));
    };

    Post.prototype.serialize = function() {
      return "message=" + this.get('message');
    };

    Post.prototype.isAuthor = function(user) {
      if (the_user.isAnonymous()) return false;
      return this.get("name") === user.get("name");
    };

    Post.prototype.mentions = function(user) {
      if (the_user.isAnonymous()) return false;
      return this.get("message").toLowerCase().indexOf(user.get("name").toLowerCase()) >= 0;
    };

    Post.prototype.formattedMsg = function() {
      return "<p>" + this.get("message").replace(/\n\n/g, "</p><p>").replace(/\n/g, "<br/>") + "</p>";
    };

    Post.prototype.eid = function() {
      return "post-" + this.cid;
    };

    Post.prototype.validate = function() {
      var msg;
      msg = this.get("message");
      if (msg.replace(/\s/g, '').length < 3) return "Message too short";
      if (msg.split(/\s/g).length - 1 === msg.length) {
        return "Will not accept blank message.";
      }
    };

    return Post;

  })(Backbone.Model);

}).call(this);
