app = require('express').createServer()

app.get '/', (req, res) ->
  res.send 'hello world'


app.listen 3000
