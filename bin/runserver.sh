###
 # @Date: 2023-01-11 14:57:36
 # @LastEditors: ThetisEliza wxf199601@gmail.com
 # @LastEditTime: 2023-01-11 15:18:41
 # @FilePath: /outlier/bin/runserver.sh
### 

if [ ! -d "tmp" ];then
    echo "create dir tmp"
    mkdir tmp
fi

if [ ! -d "log" ]; then
    echo "create dir log"
    mkdir log
fi

nohup python3 src/server.py -l INFO -lh log/app > /dev/null 2>&1 &
echo $! > tmp/pid.txt
echo "[Done] Server starts successfully on pid $!"


