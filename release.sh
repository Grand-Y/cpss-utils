#!/bin/bash

host="fdse@10.176.34.90"
read -s -p "请输入90服务器密码: "  pw


/usr/bin/expect << EOF
set timeout 15
spawn ssh $host 
expect "*password*"                 
send "$pw\r"
expect "*login*"   # 期待ssh提示 Last login:
send "rm -rf /home/fdse/sctap-frontend/dist\r" 
expect ""
send "logout\r"
expect eof

spawn scp -r ./dist $host:/home/fdse/sctap-frontend/dist
expect "*password*" 
send "$pw\r" 
expect eof

EOF
