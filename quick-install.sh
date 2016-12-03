mkdir ./plugins/map/maps/source
wget --no-check-certificate https://almsaeedstudio.com/download/AdminLTE-master
unzip AdminLTE-master
mv AdminLTE-2.3.7/plugins/ core/index/adminlte_plugins/
rm -rf AdminLTE-master
rm -rf AdminLTE-2.3.7
for d in ./core/*/ ./plugins/*/ ; do (cd "$d" && if [ -f ./package.json ]; then npm install; fi); done