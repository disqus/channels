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
      "$(document).ready(function(){\n        $(\"form#my_form\").submit(function(){\n            setTimeout(function() {\n                $('input').attr('disabled', 'disabled');\n                $('a').attr('disabled', 'disabled');\n            }, 50);\n        })\n    });\n        #$('.new-reply button[type=submit]').bind 'click', this.submit\n        $('.new-reply form').submit () =>\n            $('button[type=submit]', this).click () ->\n                console.log this\n                this.attr \"disabled\", \"disabled\"\n                false\n            false";
    }

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
