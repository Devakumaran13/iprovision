MIME-Version: 1.0
Content-Type: multipart/mixed; boundary="==MYBOUNDARY"

--==MYBOUNDARY==
Content-Type: text/x-shellscript; charset="us-ascii"

#install git
sudo yum install git -y
set -o xtrace
# replace daemon.json and restart docker
sudo cp daemon.json /etc/docker/daemon.json
sudo systemctl deamon-reload
sudo systemctl restart docker
# fetch the clustername and nodegroup name from ec2-instance tags
TOKEN='curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600"'
HEADER="--header='X-aws-ec2-metadata-token: $TOKEN'"
CLUSTER="eks:cluster-name"
NODEGROUP="eks:nodegroup-name"
INSTANCE_ID='wget -qO- --header="X-aws-ec2-metadata-tocken: $TOKEN" http://169.254.169.254/latest/meta-data/instance-id'
REGION='wget -qO --header='X-aws-ec2-metadata-tocken: $TOKEN" http://169.254.169.254/latest/meta-data/placement/availability-zone | sed -e 's:\([0-9][0-9]*\)[a-z]*\$:\\1:'
CLUSTER_NAME="'aws ec2 describe-tags --filters "Name=resource-id,Values=$INSTANCE_ID" "Name=key,Values=$CLUSTER" --region $REGION --output=text | cut -f5'"
NODEGROUP_NAME="'aws ec2 describe-tags --filters "Name=resource-id,Values=$INSTANCE_ID" "Name=key,Values=$NODEGROUP" --region $REGION --output=text | cut -f5'"
/etc/eks/bootstrap.sh $CLUSTER_NAME --kubelet-extra-args '--node-labels=nodegroup=$NODEGROUP_NAME'
echo "net.ipv4.conf.default.rp_filter = 0" | tee -a /etc/sysctl.conf
echo "net.ipv4.conf.all.rp_filter = 0" | tee -a /etc/sysctl.conf
sudo sysctl -p
sleep 45
# By default ec2-instance will have only eth0 interface. Lambda function has been used to attach eh1 and eth2 with multus subnet
ls /sys/class/net/ > /tmp/ethList;cat /tmp/ethList | while read line ; do sudo ifconfig $line up; done
grep eth /tmp/ethList | while read line ; do echo "ifconfig $line up" >> /etc/rc.d/rc.local; done
systemctl enable rc-local
#GTP installation steps
export url='http://ec2-54-185-152-150-.us-west-2.compute.amazonaws.com:8081/repository/tools/cluster/gtp5g'
export kernel_version='(uname -r)'
export CURRENT_VERSION=$(uname -r | cut -c1-4)
export VERSION_LIMIT=5.3
function ver { printf "%03d%03d%03d%03d" $(echo "$1" | tr '.' ' ');}
if [$(ver $CURRENT_VERSION) -gt $(ver $VERSION_LIMIT)]; then
    echo " Kernel version: $CURRENT_VERSION > Version Limit: $VERSION_LIMIT "
        if ( curl -o/dev/null -sfI "$url/gtp5g.ko_$kernel_version" ); then
            /etc/os-release
        if [[ $NAME == "Ubuntu" ]]; then
            sudo apt-get update -y && sudo apt-get install git -y && sudo apt-get install gcc -y && sudo apt-get install make -y
        fi
        if [[ $NAME == "Amazon Linux" ]]; then
            sudo yum install git -y
        fi
            mkdir gtp5g
            cd gtp5g
            curl -o gtp5g.ko $url/gtp5g.ko_$kernel_version
            curl -o Makefile $url/Makefile
            sudo make install
        else
            /etc/os-release
            if [[ $NAME == "Ubuntu" ]]; then
                sudo apt-get update -y && sudo apt-get install git -y && sudo apt-get install gcc -y && sudo apt-get install make -y && git clone https://github.com/free5gc/gtp5g.git && cd gtp5g && make install
                curl -v -u admin:coeadmin124 --upload-file gtp5g.ko $url/gtp5g.ko_$kernel_version
            fi
            if [[ $NAME == "Amazon Linux" ]]; then
                sudo yum install git -y && sudo yum install -y "kernel-devel-uname-r == $(uname -r)" && git clone https://github.com/free5gc/gtp5g.git && cd gtp5g && make install
                curl -v -u admin:coeadmin124 --upload-file gtp5g.ko $url/gtp5g.ko_$kernel_version
            fi
        fi
    else
        echo "Kernel version: $CURRENT_VERSION < Version Limit: $VERSION_LIMIT gtp driver will not be supported"
    fi

    --==MYBOUNDARY==--

