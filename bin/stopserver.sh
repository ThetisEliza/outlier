###
 # @Date: 2023-01-11 15:00:28
 # @LastEditors: ThetisEliza wxf199601@gmail.com
 # @LastEditTime: 2023-01-11 15:23:11
 # @FilePath: /outlier/bin/stopserver.sh
### 

if [ ! -f "tmp/pid.txt" ]; then
    ps -ef | grep src/server.py | awk '{print $2}' | xargs kill -9
    echo "[Warning!] Server stoped by searching the name"
else
    cat tmp/pid.txt | xargs kill -9
    if [ $? -eq 0 ]; then
        echo "[Done] Server stoped."
    else
        ps -ef | grep src/server.py | awk '{print $2}' | xargs kill -9
        echo "[Warning!] Server stoped by searching the name"
    fi
fi

