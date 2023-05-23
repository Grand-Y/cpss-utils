import pika

# RabbitMQ服务器的地址和端口
host = '10.177.29.226'
port = 5672

# RabbitMQ服务器的用户名和密码
username = 'admin'
password = 'admin'

# 虚拟主机名称
virtual_host = 'em_vhost'

# 建立连接
credentials = pika.PlainCredentials(username, password)
parameters = pika.ConnectionParameters(host, port, virtual_host, credentials)
connection = pika.BlockingConnection(parameters)

# 创建RabbitMQ管理对象
channel = connection.channel()


with open('location.txt', 'r') as f:
    locations = f.readlines()
locations = [x.strip() for x in locations]

with open('event.txt', 'r') as f:
    events = f.readlines()
events = [x.strip() for x in events]


# 获取所有队列和Exchange的名称
names = [e + '.' + l for e in events for l in locations]

# 删除队列和Exchange
for name in names:
    channel.queue_delete(queue=name)
    channel.exchange_delete(exchange=name)

# 关闭连接
connection.close()
