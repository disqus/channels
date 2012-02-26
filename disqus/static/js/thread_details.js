(function() {
  var Details;

  Details = (function() {

    function Details() {
      var _this = this;
      this.scrollBottom();
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
      }, "slow");
    };

    return Details;

  })();

  $(document).ready(function() {
    return new Details();
  });

}).call(this);
