Disqus = {};

Disqus.prettyDate = function(date_str) {
    // we need to zero out at CST
    var time = Date.parse(date_str);
    var now = new Date();
    var now_utc = Date.UTC(
        now.getUTCFullYear(),
        now.getUTCMonth(),
        now.getUTCDate(),
        now.getUTCHours(),
        now.getUTCMinutes(),
        now.getUTCSeconds()
    );

    var seconds = (now_utc - time) / 1000;
    // var offset = (new Date().getTimezoneOffset() - 300) * 60;
    // seconds = seconds + offset;
    var token = 'ago';
    var time_formats = [
      [60, 'just now', 'just now'], // 60
      [120, '1 minute ago', '1 minute from now'], // 60*2
      [3600, 'minutes', 60], // 60*60, 60
      [7200, '1 hour ago', '1 hour from now'], // 60*60*2
      [86400, 'hours', 3600], // 60*60*24, 60*60
      [172800, 'yesterday', 'tomorrow'], // 60*60*24*2
      [604800, 'days', 86400], // 60*60*24*7, 60*60*24
      [1209600, 'last week', 'next week'], // 60*60*24*7*4*2
      [2419200, 'weeks', 604800], // 60*60*24*7*4, 60*60*24*7
      [4838400, 'last month', 'next month'], // 60*60*24*7*4*2
      [29030400, 'months', 2419200], // 60*60*24*7*4*12, 60*60*24*7*4
      [58060800, 'last year', 'next year'], // 60*60*24*7*4*12*2
      [2903040000, 'years', 29030400], // 60*60*24*7*4*12*100, 60*60*24*7*4*12
      [5806080000, 'last century', 'next century'], // 60*60*24*7*4*12*100*2
      [58060800000, 'centuries', 2903040000] // 60*60*24*7*4*12*100*20, 60*60*24*7*4*12*100
    ];
    var list_choice = 1;

    if (seconds < 0)
    {
        seconds = Math.abs(seconds);
        token = 'from now';
        list_choice = 2;
    }

    for (var i=0, format; (format = time_formats[i]); i++) {
        if (seconds < format[0])
        {
            if (typeof format[2] == 'string')
                return format[list_choice];
            else
                return Math.floor(seconds / format[2]) + ' ' + format[1] + ' ' + token;
        }
    }
    return time;
};

Disqus.prettyDates = function() {
    $('.pretty-date').each(function(_, el){
        var $el = $(el);
        var title = $el.attr('title');
        if (title) {
            var date = Disqus.prettyDate(title);
            if (date) {
                $el.text(date);
            }
        }
    });
};

$(document).ready(function(){
    // Update date strings periodically
    setInterval(Disqus.prettyDates, 5000);
    Disqus.prettyDates();
});