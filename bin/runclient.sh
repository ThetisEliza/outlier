###
 # @Date: 2023-01-10 19:28:15
 # @LastEditors: ThetisEliza wxf199601@gmail.com
 # @LastEditTime: 2023-01-12 14:21:12
 # @FilePath: /outlier/bin/runclient.sh
### 

name=$1

git fetch origin
git checkout Beta-v1.0.3
git switch -c Beta-v1.0.3
sed -i 's/localhost/43.142.129.32/g' config/config.json

python3 src/client.py -n "$name"