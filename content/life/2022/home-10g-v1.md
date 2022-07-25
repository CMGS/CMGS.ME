# 坡县家庭万兆网络计划v1.0

- date: 2022-07-25 12:16
- tags: life,home,networking
- category: life

-------------------

首先这个系列一定是有 v2.0 的，因为最近我又花了巨资开始折腾设备，只不过可能凑齐所有设备要个把月后了，所以今天先记录下我家整个万兆计划 v1.0 版本的设计和实现落地。如果有需要的朋友也可以参考这个计划来构建自家的万兆网络。

<h3>写在前面的话</h3>

当我们在讨论万兆网络的时候再琢磨花多少钱啊这种意义就不大了，要我说结论就是不仅花钱而且很花精力。理论上来说不管是中国还是坡县，1G 基本是 WAN 口标配，对家庭内部来说 2.5G/5G 的设备其实也不便宜（毕竟最终你还要折腾不是）。另外是有了 nas 后你想把 nas 当本地盘用肯定会上 nvme 加速，你这一加速内网带宽就不够了，因此你只能选择上万兆。可选设备要么就是小型企业设备，要么就是黄鱼淘货。而且如果搞 [Mikrotik](https://mikrotik.com/) 这种专业设备的话还是挺花精力的，总之这不是一件容易事。

对于坡县来说，比起中国的毛坯房可以埋光纤或者屏蔽 Cat 7 一类的网线，县里的 Condo 基本精装毫无办法，不过新一点的至少也是超 6 起步，也算有了物理的万兆基础。但要注意的是县里的强电箱一般比较奇葩，为了「更容易」操作浪费了很多设备柜的「净深」，如下图所示：

<center>![](/media/home-10g-v1/utils.jpeg "")</center>

可以看到洗衣机空间的净深是大于上面设备柜的，设备柜加了个板子在柜子中间把强电设备装在了上面。这样的坏处一是浪费了柜子净深，二是这个深度你是放不下 1U 设备的，只能选择买一些小型家用路由交换机等，自然也就达不到我的目的了。

于是，我又又又花了一笔巨资重做了整个设备柜，去掉了这个横在柜子中前部的背板，请了电工把所有强电设备后移装在了墙上（县里的电工需要持证上岗，人工费极贵）。这样前部空间就足够我放若干服务器级别的设备了。

<h3>设备选择</h3>

在我的理念里面，WIFI 6 配置 1G 有线出口就是脑子不太好使，WiFi 6在 160MHz 信道宽度下，单流最快速率为1.2Gbps，理论最大数据吞吐量9.6Gbps，你那个 1G 有线 uplink 能有啥用。就算主流的现在就做到 5.4 Gbps 也是远超千兆有线网络吞吐的，那怎么办？

不得不说 CHH 还是豪横，只要钱给够，可以看这个帖子[「真全屋万兆WIFI6? 华为AP7060DN+AC9700S-S 万兆WIFI6组网分享」](https://www.chiphell.com/forum.php?mod=viewthread&tid=2257890&extra=page%3D1%26filter%3Dtypeid%26typeid%3D736)，它指了一条用华为企业级 AP+AC 方案的明路。在 2022 的当下，华为的 [AirEngine](https://e.huawei.com/cn/products/enterprise-networking/wlan/access-controllers/airengine-9700-m) 依然是我看到的唯一选择，至于价格嘛，告辞。

因此我还是打算采用 WIFI 5 的布局，802.11ac 提供的带宽足够了，就你这小手机上基本没区别。至于电脑，我又又又又又用钞能力买了少数带万兆口的 EATX 板子，直接走万兆有线去了。未来如果像华为这种 WIFI 6 + 万兆的设备价格降下来的话，再换就是。反正 AP+AC 的结构换 AP 是个很容易的事情。

确定好 AP+AC 结构后就开始选设备，我不是折腾党，直接就选了 Unifi 的 [Dream Machine Pro](https://store.ui.com/products/udm-pro) 做主路由器，8x1G + 1G Wan + 10G Wan + 10G Lan 能满足未来出入口流量的需求（毕竟县里真的是有 10G Wan 套餐的）。8 个低速口唯一的问题就是不带 POE，用来跑一些低速设备比如 DNS 旁路由一类的也挺实用的。加上 Unifi 是软 AC，还能省一个 AC 位。

AP 的话自然就是 Unifi 的 [FlexHD](https://store.ui.com/products/unifi-flexhd?_pos=2&_sid=b943e1969&_ss=r) 了，还是因为县里都是精装修，要顶埋线的话那得下血本把房子拆成毛坯。FlexHD 就像个可乐罐子往墙上一粘，也没那么突兀。至于为啥是 WIFI 5 我也解释过了，至少当下环境下 WIFI 5 完全足够用。

本身我自己是有一台群晖 [DS1618](https://www.synology.com/en-us/support/download/DS1618+?version=7.1#system) 的，本来只能在 10G NIC 和 2 NVME 二选一，没 NVME 10G 没意义，有 10G 没 NVME 也跑不满。20年闲得无聊的时候想升级到最新板载万兆的 [DS1621](https://www.synology.com/en-us/products/DS1621+) ，没想到群晖出了一款 2 NVME + 10G 的 [E10M20-T1](https://www.synology.cn/zh-cn/products/E10M20-T1)，一下子解决了这个问题。

为了主 PC 和 NAS 能跑有线万兆满速，在核心交换机选择上，既要 POE（给 AP 供电）又要万兆 Unifi 恰好有一款 [US-XG-6POE](https://store.ui.com/products/us-xg-6poe)。基本上你找这个规格的交换机只有他家有这个，4 个 RJ45 口分别是 nas, pc, AP1, AP2。所以只要未来某个时候 WIFI 6 AP 成熟后只要换 AP 就能实现全屋所有设备万兆互联。

在 DNS 和旁路由的选择上，采用了 [Odroid H2+](https://www.hardkernel.com/shop/odroid-h2plus/) 这台小机器，当时看中的就是这 2 个 2.5G 的接口，但没想到遇到了不少的坑。一个是 [Exsi](https://www.vmware.com/products/esxi-and-esx.html) 没有 Realtek 8125B 这块芯片的驱动，即便采用第三方的各种解决方案要么掉速，要么跑不到 2.5G。换成 [PVE](https://pve.proxmox.com/wiki/Main_Page) 后由于芯片太新，走 PCI Passthrough Ubuntu 又识别不了，得更新内核到 5.10+，还时不时抛出一些内核错误。总之计划很宏大，现实很骨感，最后旁路由也没跑，就跑了个 nginx, plex 和 dns。这个 Plex 还没法用上服务端解码 4K，毕竟 CPU 太弱了。所有进我家内网应用的流量会打到了 nginx，配置好了 letsencrypt 后全内网 https 化。

最后整个拓扑图如下：

<center>![](/media/home-10g-v1/topology.jpeg "")</center>

<h3>尾声</h3>

至此整个第一代万兆局域网完工，但由于 Odorid H2+ 的问题 AIO 实际上没有起到 All in one 的作用。比如我想跑 [Home Assistant](https://www.home-assistant.io/) 就搞起来比较麻烦，毕竟 CPU 也菜得抠脚。当然布局也是比较奇葩，所有的设备都丢在强电箱空间内，买了个 PWM 调速器，接上了之前 PC 换下来的 3 个 14mm PC 风扇散热，环境非常恶劣。得亏这群设备耐操，目前运行一切正常。

<center>![](/media/home-10g-v1/real.jpeg "")</center>

于是苟了 2 年后，大规模升级开始了！