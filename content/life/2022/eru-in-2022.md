# Eru in 2022

- date: 2022-03-28 12:16
- tags: work,golang,dev,docker
- category: life

-------------------

> 现在可以说 k8s 也不过如此了

我在前年写下 [Eru in 2020](https://cmgs.me/life/eru-in-2020) 的时候我也没想到它的续集要到 2022 才有，而且是在我离职之后。我依然感激历史的进程成就了 [Eru](https://github.com/projecteru2)，也证明其实不跟 CNCF 也没啥，整体成本还更低。满打满算人力 3+1，全量集群 > N0K nodes（N > 2)，单一 Eru Core 管理 > 5K nodes（这也是一个 k8s 典型集群上限，borg 的中位数是 10K，而我们很接近），并且横跨多地（洲际）。当然随着我的离职它未来的命运可能多舛，101 们又不懂 infra 砍腿在北京扩团队换 k8s 也是正常。但无所谓了，Eru 现在是一个整体解决方案，也有了第三代目的 Core Maintainer，我这几年的努力也算没有白花，只希望未来在某个地方它能真正实现大一统架构吧。

毕竟，作为 infra builder，大一统架构是我最后追求的东西了。

### 状态

目前 Eru Projects 是包含了很多子项目的一个整体解决方案，毕竟我们追求的是大一统，而不是单纯的 PaaS 或者是容器调度罢了。包括不仅限于：

1. [Core](https://github.com/projecteru2/core)
2. [Agent](https://github.com/projecteru2/agent)
3. [Cli](https://github.com/projecteru2/cli)
4. [Barrel](https://github.com/projecteru2/barrel)
5. [Yavirt](https://github.com/projecteru2/yavirt)
6. [Pistage](https://github.com/projecteru2/pistage)
7. [Docker-cni](https://github.com/projecteru2/docker-cni)
8. [Systemd-runtime](https://github.com/projecteru2/systemd-runtime)

毕竟作为大一统的架构，多种运行时调度是必须的，而且在这过程中我们还是顺手的解决了 Container 的一些问题，比如 Fixed IP，比如 CNI support 等。

在第三代目 Core Maintainer 的 [Resource Plugin](https://github.com/projecteru2/core/pull/491) 最终 Review 和合并后，Eru 本身的调度将拥有无限制资源维度扩展能力，这个资源可以是硬件资源，也可以是 Software Defined Resource 比如 K8s 里面的亲和性逻辑等。比起 K8s 的 Extend Resource 这个机制更加强大和灵活。加上本身 Eru 拥有[「赤道上最好的 CPU 调度逻辑」](https://github.com/projecteru2/core/issues/339)，支持 NUMA，支持 Local Volume 等多维度资源调度分配能力，老实说资源调度这块我们还是有信心说出这句「 k8s 也不过如此」的。

另外值得一提是 [Agent](https://github.com/projecteru2/agent) 本身也将迎来新的重构，虽然目前它已经[支持](https://github.com/projecteru2/agent/pull/73) 虚拟机监控了但我们觉得还是可以再改吧改吧的。旁路系统的好处就是系统不管怎么崩对业务没有什么影响，2020 的时候我说过只有 2 次事故，而到了 2022 依然还是这 2 个。

### 关于容器的一切

Eru 毕竟是靠着编排调度容器起家，因此过去 2 年我们还是做了不少容器方向工作了，其一就是彻底解决容器 Fixed IP 的问题。

从原理上来说容器其实就是进程的 namespace 展开，读过《三体》都知道质子的二维展开，本质上其实类似。进程的生命周期等同于 namespace 的生命周期，这也是为什么 docker 无法区分 stop 和 remove 的原因 ———— 本质上进程都停止了，namespace 都回收了，因此 IP 也就释放了。

因此传统的手段上，要么富容器结构，自定义 init 什么的跑到死，穿着裤子来控制容器内业务进程，尽可能保持容器持续运行。要么就是 k8s 这类组合形态的 Pod，专门有个一直运行的容器负责 namespace，真实业务进程通过 join 的方式共享 namespace 里面的一切，当然也就包含 IP。

但无论哪种方式，依然没有解决如果这个 Pod 或者这个容器 Stop 之后 IP 还是会回收怎么办这个问题。所以我们决定从网络插件入手，说起来可以追溯到我修改过的最后一个版本的 [Calico-libnetwork-plugin](https://github.com/projectcalico/libnetwork-plugin/pull/183)，但和传统自定义 CNI/CNM 不一样的在于，我们决定给 Docker 套层壳，于是我们就有了 [Barrel](https://github.com/projecteru2/barrel) 这个项目。其核心逻辑是区分 Stop 和 Remove 行为，遇到 Stop 的请求则把 IP 放到另外一个地方而不是回到 IP Pool，遇到 Remove 再真正去 Release IP。当然有人就要问了，为啥不直接改插件呢，这就涉及到我们未来的规划，我们其实还是想基于 [containerd](https://containerd.io/) 实现自己的容器 runtime 的，因此做 wrapper 的话更合适，方便未来的迁移。

另外就是 Docker 对 CNI 的支持，在 K8s 崛起之后 Docker 以及它提出的标准基本都不太行了，其中就包括 CNM 接口。Calico 很早就放弃了 libnetwork plugin 的维护，我们于是决定去支持 CNI。但明显 Eru 不是 CNCF 那种「Cloud Native」的玩意，想要在 Docker 上去支持 CNI 就需要废一些周折，于是在第二代目 Core Maintainer 的努力下，于是我们有了 [Docker-cni](https://github.com/projecteru2/docker-cni) 这个项目，通过 oci 的 hook，使得 Docker 原生也能正常使用 CNI 的插件，从而实现生命的大和谐。

而这两个项目如果一帆风顺大概率是会 Merge 在一起的，最终发展成某个有着 fancy 名字的容器运行时，只不过目前应该看不到这天了吧。 

### 关于大一统的其他引擎

I have a dream that one day 哦不好意思串场了，但作为 infra builder 大一统架构确实是很多人想实现的。比如前司既搞 k8s 又想搞 openstack 这种听起来就觉得不够 fancy ，而且他们也没解决网络控制面和转发面的统一。而我们的组使用 Eru 所做的业务已经有了大一统的雏形了，支持容器，支持虚拟机，支持裸进程等。

虚拟机的实现 [Yavirt](https://github.com/projecteru2/yavirt) 和传统 [kubevirt](https://kubevirt.io/) 和 [virtlet](https://github.com/Mirantis/virtlet) 不一样的在于，它既不像后者那样需要一个容器的 namespace 辅助提供网络接入手段（其实前者也有类似情况，VMI 的 POD 提供网络等资源），也不像前者一样 VM:VMI 1:1 这样浪费资源，同时使用的接口和传统 k8s 的接口还不一样（毕竟是 CRD 扩展出来的资源）。更重要的是根据 [KISS 原则](https://zh.wikipedia.org/zh/KISS%E5%8E%9F%E5%88%99)，Yavirt 是可以脱离 Eru 运行的，就像 Docker 一样。

你看虽然大家都是围着 libvirt 玩的魔法，但确实玩得都不一样。Yavirt 在前司落地之后服务了近百个团队，提供了原生的容器支持，最重要的是它的网络控制面和转发面是和容器引擎统一的，在最新的实现中都是基于 CNI interface。某种意义上来说不管是哪种网络，不管是哪种运行环境，Yavirt 都可以做到和容器侧的互通。

全功能（HOT/COLD Mirgration，DISK Bind，IOPS Guaranteed 等），傻子都能用的高效独立 VM Engine，这是我们向大一统架构迈出的很重要一步。原计划是 RDS 整个服务都用它不过按照现在这光景，难了。

至于对 systemd 的[支持](https://github.com/projecteru2/systemd-runtime)还处于社会主义初级阶段，但通过对 containerd 的 hook 我们依然可以在目前的版本上实现对机器上任意裸进程的控制，包括接入 SDN，还是蛮像 [systemd-nspawn](https://www.freedesktop.org/software/systemd/man/systemd-nspawn.html) 的。不过讲实话我们搞这个项目的时候就发现 systemd 功能真是多，namespace，chroot 啥的都有，得空做一个 systemd version 的 docker 也不是不可能。

### 其他

Eru 最让人诟病的是没有 PaaS 能力，当然我们在前司还是搞了一些东西来加强这部分的，比如 Zero Framework 什么的，提供基于 Action 模式的操作模板。当然又有人说了，Operator 这种基于状态自持的方式才是当今主流，我只想说白猫黑猫，抓到耗子的才是好猫。Operator 的方式本身对状态的控制就有着更加严格的要求，同时对于一个 Operation 颗粒度也需要更加细心的切割。Action 嘛，猛操干就完了，状态不一致怎么办，修呗。其实我个人观点是真没那么多非黑即白的，达成目标就行了。

在 [Eru in 2020](https://cmgs.me/life/eru-in-2020) 中我提到过有个朋友在帮我们做一个 Pipe Workflow 的项目，类似于 K8s 的 [Argo](https://github.com/argoproj/argo)，而这个项目去年也从他的 namespace 下 transfer 了到 Eru 这边，这就是 [Pistage](https://github.com/projecteru2/pistage)。与之前计划的不同在于，Pistage 更像是一个 Github Action 结合 Gitlab CI 的东西，不过 ETL 的玩意大多如此，也没什么好说的了。

我们本来是计划在 2022 年全面重构内部业务 Controller 转为这种模式的，毕竟 Github Action 是真好用，也非常适合中间件这种业务形态，不过目前不好说了，只能走一步算一步吧。

### 未来

> 马卡洛夫：苏联、党中央、国家计划委员会、军事工业委员会和九个国防工业部。600个相关专业、8000家配套厂家，总之需要一个伟大的国家才能完成他

马卡洛夫有没有说过这句话其实我不知道，但 infra 在软件工程上和军事上造航母也差不太多，一个好的平台是离不开公司层面鼎力支持的。我经历过豆瓣的 DAE，当时可以说是教授捧着这个项目上去的。我也经历过芒果TV，一朝皇帝一朝臣，就像现在一样。在前司内 Eru 的未来已经黯淡，作为搞了 infra 几十年的我来说，你问我愿不愿意看到它的结束我当然是不愿意的，但这就是历史的车轮吧，和个人奋斗真无关。

恰好我来了前司，恰好前司啥都没，恰好前司因为一些问题不准用 k8s，恰好没人搞中间件这锅甩给了我，恰好我搞的 Eru …… 太多机缘巧合之下 Eru 成为了前司至少在目前最重要的基础设施。当然 Eru 也不负众望，用更低的成本，更高的效率，被验证过的超大集群规模支持了前司过去几年的高速发展。未来会怎样，我现在说了也不算了，毕竟 101 们要求闭源的同时也在谋求迁移到他们自己搞的 k8s，反正不是自己的钱不心疼呗。我也不看好一群没搞过 infra 的人拍着脑袋指指点点闭源的 Eru 能做出什么新花样，毕竟当我们的 Volume Binding 都落地这么久后，还能拍着脑袋告诉团队你们要不要做绑定本地盘来保证 IOPS 玩意能有多少水平，大家心里也有数。

如果硬要我说的话，只有伟大的公司才配有大一统的基础架构，工作嘛最重要的就是开心。天下无不散之筵席，是时候江湖再见了，我只能说：

**Good Luck**
