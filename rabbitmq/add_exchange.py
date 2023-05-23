import pika

# RabbitMQ服务器的地址和端口
host = '10.177.29.226'
port = 5672

# RabbitMQ服务器的用户名和密码
username = 'admin'
password = 'admin'

# 虚拟主机名称
virtual_host = 'em_vhost'

# 读取location.txt和event.txt文件，生成队列和Exchange的名称列表
with open('location.txt', 'r') as f:
    locations = f.readlines()
locations = [x.strip() for x in locations]

with open('event.txt', 'r') as f:
    events = f.readlines()
events = [x.strip() for x in events]

queue_names = [e + '.' + l for e in events for l in locations]
exchange_names = queue_names


# 建立连接
credentials = pika.PlainCredentials(username, password)
parameters = pika.ConnectionParameters(host, port, virtual_host, credentials)
connection = pika.BlockingConnection(parameters)

# 创建RabbitMQ管理对象
channel = connection.channel() 

# 创建Exchange
for exchange_name in exchange_names:
    channel.exchange_declare(exchange=exchange_name, exchange_type='fanout', durable=True)

# 创建Queue并绑定到Exchange
for queue_name in queue_names:
    location, event = queue_name.split('.')
    exchange_name = queue_name
    channel.queue_declare(queue=queue_name, durable=True)
    channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key=queue_name)

# 关闭连接
connection.close()
