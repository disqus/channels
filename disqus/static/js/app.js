(function() {
  var Test;

  Test = (function() {

    function Test() {}

    Test.prototype.test = function() {
      return alert("OK");
    };

    return Test;

  })();

}).call(this);
