# Docker network on cloud

- date: 2015-12-22 15:20
- tags: docker,work
- category: life

-------------------

花了一天时间对云上的几种网络方案做了一个测试。做这个测试呢主要是因为某位不愿意透露姓名的公司现在完全依赖于 ucloud，为了以后上班能偷懒，方案上得先行一步。另外一点是做了大量 Google 搜索之后能找到的信息太少了，无论是国内还是国外。有点像 2010 年 Gevent 刚问世的情况一样 ，并没有各种方案之间的完整对比测试，能找到的几个报告都比较老了，所以就自己详细测了一发。

机器配置 Ucloud 1Core 1G VxLAN offload off (fixed) 允许 BGP 广播   
测试参数 qperf -oo msg_size:1:64K:*2 $IP tcp_bw tcp_lat   
CPU 压力主要看 load，最终排名是   
host &lt; calico(bgp) &lt; calico(ipip) = flannel(vxlan) = docker(vxlan) &lt; flannel(udp) &lt; weave(udp)

由于不知道什么鬼的原因，没测 weave fast-data-path 然而我看了下 weave 的实现，觉得没多大必要，大概最终性能也就介于 flannel(vxlan) 和 flannel(udp) 之间   
裸网卡性能比 1G 的要快，iperf 的实测是 2.4G，估计是做了多路网卡融合。

具体结果如下图

<center>![带宽](/media/2015/docker-network-cloud/1.jpg "带宽")</center>
<center>![延迟](/media/2015/docker-network-cloud/2.jpg "延迟")</center>

weave(udp) 真是惨，生产环境就别考虑了。看了下他们的架构，觉得即便是 fast-data-path 也没多大意义。   
**优势**：无   
**劣势**：就是个渣渣，概念好毛用都没   

calico 的 2 个方案都有不错的表现，其中 ipip 的方案在 big msg size 上表现更好，但蹊跷是在 128 字节的时候表现异常，多次测试如此。bgp 方案比较稳定，CPU 消耗并没有 ipip 的大，当然带宽表现也稍微差点。不过整体上来说，无论是 bgp 还是 ipip tunnel，calico 这套 overlay sdn 的解决方案成熟度和可用度都相当不错，为云上第一选择。   
**优势**：性能衰减少，可控性高，隔离性棒   
**劣势**：操作起来还是比较复杂，比如对 iptables 的依赖什么的（老子不是 SA ！！！）   

flannel 的 2 个方案表现也凑合，其中 vxlan 方案是因为没法开 udp offload 导致性能偏低，其他的测试报告来看，一旦让网卡自行解 udp 包拿到 mac 地址什么的，性能基本上可以达到无损，同时 cpu 占用率相当漂亮。udp 方案受限于 user space 的解包，仅仅比 weave(udp) 要好一点点。好的这一点就是在实现方面更加高效。   
**优势**：部署简单，性能还行，可以兼容老版本 docker 的启动分配行为，避免 launcher   
**劣势**：没法实现固定 IP 的容器漂移，没法多子网隔离，对上层设计依赖度高，没有 IPAM，对 docker 启动方法有绑定   

docker 原生 overlay 方案，其实也是基于 vxlan 实现的。受限于 cloud 上不一定会开的网卡 udp offload，vxlan 方案的性能上限就是裸机的 55% 左右了。大体表现上与 flannel vxlan 方案几乎一致。   
**优势**：docker 原生，性能凑合  
**劣势**：对内核要求高（&gt;3.16, 当然新版已经不做要求），对 docker daemon 有依赖需求 ( consul / etcd )，本身驱动实现还是略差点，可以看到对 cpu 利用率和带宽比同样基于 vxlan 的 flannel  要差一些，虽然有 api 但对 network 以及多子网隔离局部交叉这种需求还是比较麻烦，IPAM 就是个渣  

综上，云上能用 BGP 就果断上 calico bgp 方案，不能用 BGP 也可以考虑 calico ipip tunnel 方案，如果是 coreos 系又能开 udp offload，flannel 是不错的选择。docker network 还有很长一段路要走，weave 就去死吧。

最后，放一个在物理机上测试 macvlan 和裸网卡的对比图，1G 带宽的物理机。

<center>![macvlan](/media/2015/docker-network-cloud/3.jpg "macvlan vs host")</center>

呵呵哒，退云保平安，亿万 macvlan 平带宽……
