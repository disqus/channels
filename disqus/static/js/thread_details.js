(function() {
  var Details;

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
          _this.submit();
          return false;
        }
      });
    }

    Details.prototype.submit = function() {
      return $('form')[0].submit();
    };

    Details.prototype.scrollBottom = function() {
      return $('body').animate({
        scrollTop: $(document).height()
      }, 0);
    };

    return Details;

  })();

  $(document).ready(function() {
    return new Details();
  });

}).call(this);
