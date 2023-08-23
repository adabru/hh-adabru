http = require('http')
fs = require('fs')
path = require('path')
url =  require('url')

let config = {
  port: 2222,
  host: '::1',
  baseurl: ''
}
for (let arg of process.argv.slice(2)) {
  let [key, value] = arg.split('=')
  key = key.substring('--'.length)
  config[key] = value
}
// if (!config.token) {
//   console.log('usage:\n    node server.js --token=TOKEN [--port=2222] [--baseurl=]\n')
//   return
// }

var comments
try {
  comments = JSON.parse(fs.readFileSync('comments'))
} catch (e) {
  if (e.code == 'ENOENT') {
    fs.writeFileSync('comments', '[]')
    comments = []
  } else {
    throw e
  }
}

port = process.argv[2]

var server = http.createServer( (req, res) => {
  try {
    res.on('error', e => console.error(e))
    req.on('error', e => {
      console.error(e)
      res.writeHead(500)
      res.end('error processing request')
    })
    if (req.url != path.normalize(req.url)) {
      res.writeHead(400)
      res.end('invalid path')
    } else {
      let {query, pathname} = url.parse(req.url, true)
      if (pathname.endsWith('/')) pathname += 'index.html'
      // if (query.token != config.token) {
      //   res.writeHead(401)
      //   return res.end('wrong token specified!')
      // }
      if (pathname == '/putComment') {
        res.writeHead(201)
        let chunks = []
        req.on('data', c => chunks.push(c))
        req.on('end', () => {
          try {
            let body = Buffer.concat(chunks).toString('utf-8')
            let {user, message} = JSON.parse(body)
            if (user === undefined || message === undefined) {
              res.writeHead(400)
              return res.end('missing user or message in request body')
            }
            comments.push({user, message})
            fs.writeFile('comments', JSON.stringify(comments, null, '  '), (err) => {
              if (err) {
                res.writeHead(500)
                res.end('failed saving comment')
              } else {
                res.writeHead(200)
                res.end('ok')
              }
            })
          } catch (e) {
            res.writeHead(500)
            res.end('failed saving comment')
          }
        })
      } else if (pathname == '/getComments') {
        res.writeHead(200)
        res.end(JSON.stringify(comments))
      } else {
        fs.createReadStream(`.${pathname}`)
          .on('error', () => {
              res.writeHead(404)
              res.end('not found')
            })
          .on('open', () => {
            contenttypes = {
              '.js': 'application/javascript',
              '.css': 'text/css',
              '.styl': 'text/css',
              '.svg': 'image/svg+xml',
              '.png': 'image/png',
              '.jpg': 'image/jpg',
              '.pdf': 'application/pdf',
              '.html': 'text/html',
              '.htm': 'text/html'
            };
            // 'Content-Type': 'text/html; charset=utf-8'
            res.writeHead(200, {'Content-Type': contenttypes[path.extname(pathname)] || 'text/plain'})})
          .pipe(res)
      }
    }
  } catch (e) {
    console.error(e)
    res.writeHead(500)
    res.end('server error')
  }
})

server.listen(config.port, config.host, () => console.log(`http-server running at http://${config.host}:${config.port}/`))

server.on('error', e => {
  console.log('An error occured while serving: ' + e)
  setTimeout(() => {
      server.close();
      server.listen(config.port, config.host);
    }, 1000)
})

process.on('SIGINT', function () {
  try { server.close() }
  catch(e) { }
  process.exit()
})
