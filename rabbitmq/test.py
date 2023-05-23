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

# 检查连接状态
if connection.is_open:
    print('RabbitMQ连接成功')
else:
    print('RabbitMQ连接失败')

# 关闭连接
connection.close()
