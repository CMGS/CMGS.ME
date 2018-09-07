# 容器战争

- date: 2018-4-22 17:52
- tags: docker,work
- category: life

-------------------

引子
====

在前东家写完了 [Eru2](https://projecteru2.gitbook.io/white-paper/) 之后，花了很长一段回顾过去 4 年容器圈的发展，学习其他系统的经验。一方面 [CNCF](https://www.cncf.io) 崛起之快令人难以置信，短短几年已经成为不亚于 [ASF](http://www.apache.org/) 的存在，在各种 conference 上面不遗余力强推自己的项目，或撕逼，隐约有一统江湖之势。另一方面 [kubernetes](https://kubernetes.io/) 的调度编排战争已经几乎打完，依托于 CNCF 的推广和已经成为了事实的标准的 CNI/CRI 等接口规范，隔壁亲家 [Docker](https://www.docker.com/) 的核心组件拆的拆（[containerd](https://github.com/containerd/containerd)），「无奈」内置 CRI 实现的，逐步抛弃 CNM 模型等，完全毫无招架之力，拆得只剩个 bug 略多的 daemon。更别说亲儿子 Swarm 的下场了，丧权辱国的直接接上 K8s。也就 ASF 下的 [Mesos](http://mesos.apache.org/) 还能吊着一口气。但那不争气的 [Marathon](https://mesosphere.github.io/marathon/) 啊，看看隔壁 K8S 的生态，What can I say。

有意思的是 16 年我写 [Docker 的未来](http://cmgs.me/life/docker-in-feature) 的时候还被人「教育」过不懂 Docker，不好意思你大爷还是你大爷。现在来看 [cri-o](http://cri-o.io/)、[rkt](https://coreos.com/rkt/) 甚至 Docker 自己的 containerd 发展趋势，只能回一个关爱智障的微笑并手动再见。就连经过了大量生产验证的老牌网络组件 [calico](https://www.projectcalico.org/) 都已在 3.X 版本之后不再维护和更新 libnetwork CNM 模型下的 docker 网络接口，去掉了对 Mesos 的支持，还说战争没打完的不是蠢就是坏。

毫无疑问战争已打完了，CNCF 天量资金加持下的 k8s 赢得了天下，但它真的就无懈可击么？

人！人！人！
=========

不可否认 k8s 是一个非常不错的系统，无论是调度编排这个层面还是宏观上架构设计层面。你可以说早期的 k8s 就是娘不亲爹不爱就那么几个工程师打着 Google 旗号在开源界见缝插的这个针。无奈是猪对手加 G 家光环，我一个~~图书管理员~~开源系统怎么就做到了世界之王呢？

个人看来还是因为 G 家光环太过于耀眼。

前有 Mapreduce GFS bla bla 大量工业界论文，后有神乎其神的 Borg 把编排说得出花。大多数人选型的时候一看哟 G 家的东西啊，上上上，然后就没然后了。再加上对手实在是不够打，比如 Mesos 至今周边无论是语言还是完善度都不统一（当然你可以说它两层结构注定的），再比如愚蠢的 Swarm mode 助攻。人又不傻，有爹的东西当然最好啦。

然而我很不想说的是，每一家的东西无论开源与否都是立足于自身业务上的，这一点上真不是用了 G 家的东西就会让你的团队成为 G 家的一毛一样的工程师，感觉上就和 G 家平起平坐了。手头有什么牌就打什么牌，能赢那是技术好，但一对三真的干不过四个二的。

我见过大多数用 k8s 的团队，很大程度上都是把 k8s 当黑箱用。规模小了搭建起来成本就很高，那么多概念上的东西在规模小的时候就去强加于业务真的有必要么？Pod 的设计不就是 Virtual Machine 下多进程业务在容器时代没办法的一个 Workaround，那服务治理概念一堆堆但本质上没有什么事是一个 proxy 解决不了的，有那不就再加个 proxy 么。另外规模大了这么一个大黑箱真出了什么毛病，怎么搞？我自己看 kubelet 的执行流程和实现，包括对比 cri-o rktnetes containerd docker-shim 等 runtime 实现细节想找人交流交流都很难找到。另外还有社区有更新你跟不跟，不跟有 security 问题怎么办，升级出了幺蛾子怎么搞，要知道 k8s 严格意义上可不算什么旁路编排和调度系统，升级惨案还少么？

真不是用了 G 家的东西就和 G 家工程师一个水平了。

Kubernetes 的未来
================

不管怎么说，k8s 已经成为了事实的标准。可以预见的未来里面，在 CNCF 的支持下，社区是它最深的护城河。假如你需要一个能解决容器调度编排，能解决服务治理，能链路控制(升降级，流控，发现等)，能一劳永逸开箱即用（抛开各种概念）的基础设施，它是唯一的选择，也是最好的选择。

但它实在是太复杂了，远的 Pod 不说，近一点服务治理里面的 Sidecar 概念和我单独起 SDK 中间件有啥区别。好你要说不需要语言绑定是没毛病，但比性能这种模式你也比不过 in-memory 的设计啊？

你想用 [istio](https://github.com/istio/istio) ok，上 k8s。你想用 [linkerd](https://linkerd.io/) ok，上 k8s 。拆开用是能用，但只有 k8s 下，这些东西所宣称的那些花样你才玩得溜，这和强制绑定有啥区别。hmmm，新时代的 [Apache httpd](https://httpd.apache.org/) 即视感有没有？

那么随着业务的增长，基础平台是抽象出来了，但依然需要大量人力成本去维护去学习。本来搞个平台层面的东西就想自动化压低成本，现在倒好概念能和前端界一样日新月异，个人觉得并不是什么好事情。在战争结束前 K8s 可能还没这么多争议，战争结束后众口难调的情况下只有这一个靶子，摊手。可以想象得出随着时间的增长对 K8s 复杂度的吐槽将会越来越多。同样的，我也预计不久的将来，和 Apache httpd 终究遭遇了 nginx 一样，编排和调度系统的 「nginx」也会出现在我们视野，就像老牌 Hashicrop 下的 [nomad](https://www.nomadproject.io/) 一样等待着和 K8s 平分天下。

新的战场
=======

Docker 是输了编排和调度，也失去了那种号令天下的霸权。然而对 K8s 来说最不幸的是产生容器的「工厂」标准依然在 Docker 手中。

无论是 [OCI](https://www.opencontainers.org/) 镜像标准和 Docker 镜像标准亲兄弟，还是运行层面的 containerd。K8s 整了 CRI/CNI 什么的，又扶持了 CRI-O 还有隔壁 Rkt 什么的，并没有一点卵用，看看那个 [appc](https://coreos.com/rkt/docs/latest/app-container.html) 的概念还有人提么。containerd 在最新 RC 中内置 CRI 支持，可以直接替换 kubelet 的 dockershim 实现，也把之前的 cri-containerd 丢入了历史的垃圾堆，已然成为了集大成的事实标准。

你 CRI-O 说自己测试完备率更高，高得过一直内置代码在 K8s 的 dockershim/containerd 一脉相承？你 rkt 说自己进程树扁平，能比 containerd 直接挂容器到 systemd 下更平？况且都抽象控制平面了，下面 runtime 不都是支持 runc runV 混布么。还有你一个 cri-o 别的不学，硬要去做个内置 pod 你让隔壁的 kubelet 没饭吃怎么办？

基础设施是一定图稳的，在目前换 CRI-O Rkt 等没有明显显著优势的情况下，甚至大劣的情况下，containerd 就是事实标准。Docker 回归到了他应该在的位置，那就是容器「引擎」。当然了 containerd 的成功也是依托于 K8s 的成功，随着 dockershim 的实现走进~~千家万户~~。

而随着 containerd 的日益成熟，新的编排系统，新的系统架构，也就有了新的血液。在这之上产生一个足以威胁到 K8s 的新基础设施系统，是完全可以期待的。

尾声
====

即便站在 2018 年这个时间点上，我依然认为调度和编排还是一件可以做的事情。怎么单独的用 containerd 去驱动容器，怎么解构复杂 Pod 转变为 native container （1 process 1 container）再通过上层的组合完成复杂业务形态，怎么通过 CNI 结合现有的基础网络等插件，怎么实现更高效的万台机器编排等，依然还有想象力空间。

旧的战争已经结束，新的战场已经硝烟四起。对于 containerd 的用途我个人是比较看好的。没有历史的包袱，又向下兼容各类系统的接口，稳定性经过了大量生产实践，还可以很方便的二次开发。也许过几年我们就能看到基于其新的调度编排「nginx」了吧。
