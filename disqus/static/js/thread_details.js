(function() {
  var Details;

  Details = (function() {

    function Details() {
      var _this = this;
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

    return Details;

  })();

  $(document).ready(function() {
    return new Details();
  });

}).call(this);
