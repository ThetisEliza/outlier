###
 # @Date: 2023-01-10 19:28:15
 # @LastEditors: ThetisEliza wxf199601@gmail.com
 # @LastEditTime: 2023-01-10 19:53:51
 # @FilePath: /outlier/bin/runclient.sh
### 
git fetch origin
git checkout Beta
git switch -c Beta-release 
sed -i 's/localhost/43.142.129.32/g' config/config.json

python3 src/client.py -n "you name"