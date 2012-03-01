var fs = require('fs');
var opts = {
    key : fs.readFileSync('/etc/pki/tls/certs/pycon.key'),
    cert : fs.readFileSync('/etc/pki/tls/certs/pycon.crt')
};

var bouncy = require('bouncy');
bouncy(opts, function (req, bounce) {
    if (req.url.indexOf('/socket.io/') == 0) {
        bounce(3000);
    } else {
        bounce(82);
    }
}).listen(443);
