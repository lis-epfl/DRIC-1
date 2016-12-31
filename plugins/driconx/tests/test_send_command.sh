prefix="http://localhost:9555"
url_new="$prefix/driconx/new"
url_cmd="$prefix/mavlink/command/d9e97623f3-1/520"
curl -H "Content-Type: application/json" -X PUT -d '{"type":"UDP","host":"127.0.0.1","port":14551,"binding":"mavric","connecting":true}' $url_new
curl -X POST -d 'p%5B%5D=1&p%5B%5D=&p%5B%5D=&p%5B%5D=&p%5B%5D=&p%5B%5D=&p%5B%5D=' $url_cmd