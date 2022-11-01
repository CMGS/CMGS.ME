# 离职 v1.0

- date: 2022-03-17 16:10
- tags: life,singapore,work
- category: life

-------------------

> It's the last mail from me to the SPP members.
>
> Thanks to all you guys for such a great achievement in the SPP team and supporting my work. 
>
> It is my pleasure to work with you. Hope you guys like my management in the past years.
>
> Covid 19 and reorg affected us a lot, it's true. But we still have lots of things to do, even though maybe we can not reach the vision we dreamed of, such as a unified and efficient platform to support the biggest SEA company and the intercontinental infrastructure.
>
> However, don't be sad, remember what we did in the past 2 maybe 3 years, what a great achievement. We are the best engineering team in the whole company, not like 101 and useless trash.
>
> I am proud of all of you.
>
> Don't let down your pride, keep going, fight for yourselves. Remember our motto: don't panic, we are the platform.
>
> Good luck.

这封邮件是我被立即解职（Effective now）不用交接不准做任何事情包括代码职权和面试职权的时写给全组组员的，那时候就其实已经决定离职了，后面的所有申诉+投诉都是一口气，再怎么说败犬也比舔狗好。何况这美股怎么跌其实不太影响长沙财富自由…玩个十年八年的资本还是有的，也没太多必要和给我打工的「高 P」们纠缠，发完离职邮件的那天我妈担心我不开心，我说我现在开心得要死，不用鸟那群死妈的玩意儿还可以天天魔兽打副本能不开心吗，而且现在可以躺到大吉大利，够本了。

Last Day 那天也算是头一次在一家公司呆满了 4 年，过去的一年改制后确实过得不开心，还好呆过国企芒果 TV 知道套路保留了足够多的证据，听过某次评审会录音的厂工们都理解并且支持我，也算是没白呆了。这 4 年我可对得起 Shopee 发的股票和工资，但是嘛我有我的原则，这里就讲讲过去的工作，也就不给 SG PR 团队添麻烦了。 

总的来说这几年大概就干了三件事，一个定义了公司网络拓扑。二个整了中间件苟住了所有的业务。第三个就是拉起了集团最能打的团队。如果说还有一点什么成绩，就是 Shopee 一定要做云，这个对 Shopee 的技术有很大的关系，还有就是培养人才。但这些都是次要的，我主要就是三件事情，很惭愧，就做了一点微小的工作。 

#### 在公司网络的拓扑定义上大体上干了这么些事： 

1. 硬件层面的 router-reflection 拓扑设计落地
2. 构建跨机房大规模 BGP 的 underlay SDN
3. 重写整个 [Calico-libnetwork-plugin](https://github.com/projectcalico/libnetwork-plugin/pull/183) 统一了整个容器网络控制面
4. 和不愿意透露姓名的 anrs 统一了大一统架构里面虚机/容器网络控制面和转发面
5. 低成本原生解决容器[固定 IP 问题](https://github.com/projecteru2/barrel)
6. CNM 2 CNI 的在原生 docker 上的[解决方案](https://github.com/projecteru2/barrel)

#### 整了中间件苟住了所有的业务包括不仅限于：

1. 应该是全东南亚最大的 Cache 集群，也是我知道的最大的基于 Redis Cluster 缓存集群，其实放中国能和我们掰掰手腕的也就是那几家头部了，不超过一只手。
2. 高性能的 proxy 实现，解决了流量/连接不均匀问题，而且这个实现方式非常鸡贼，比起 15 年的 redis-cerberus 和饿了么的 redis-corvus 成本更低。
3. 我们的中间件服务也许是公司口碑最好的服务，Cache 从 18 年至今最严重就发生过 2 次 P1 估计都算不上的事故，而且锅还是 eru 的。每次大促我都说，准备好机票，因为我们挂了是没有所谓 Plan B 的。大体上如果我们挂了，比某 anrs 的头条 p0 还要严重，因为基本上全公司的业务都在用 我们的中间件服务包括不仅限于 Cache，KV，RDS，ETCD 等。
4. 「异想天开」的 not redis compatible but original redis kv 设计，根据我混了这么久的互联网经验，我只能说和现在开源的 kvrocks 啦，ssdb 啦，pika 一类的啦完全不是一个路子，成本低性能好，关键是所有 redis 工具它都能用。
1. 一整套控制面工具链，无脑高效，感谢隔壁团队 STO 的支持，尤其是跟我们合作的 SRE 真是太棒了。
2. 不说全司 1/10 的机器是 Cache，1/15 肯定有，实际上真算中间件的话 10% 的机器在我名下问题不大，这些机器的资源都做到了利用率最大化。比如某宇宙级公司的 Cache 现在好像还没绑核，而我们早就是绑核，绑盘（kv），绑 NUMA （RDS）什么的支持跟玩一样（是的就是嘲讽 k8s）。

#### 集团最能打的团队包括不仅限于：

1. 我和另外一个同事 2019 年奉命建立 SPP，2 to almost 100，实线+虚线到我这差不多占一半多，其中大多数不是我 referral 就是我亲自面的，恩这可是在新加坡，过去的几年我们只进不出。
2. 公司最年轻的 P8，最年轻的 P7，谦虚一点说个人的努力当然很重要，但老板也得是个伯乐对吧。当然我一般不太谦虚，直说了就是我培养的。一个团队负责人应该是给团队兜底的，而不是应该是团队的天花板。
3. 大概是全司唯一一个从不限制休假/摸鱼/打游戏的团队，不管工作时间长短，只看结果，下班巴不得你们赶紧跑路，每个项目都做到了二级到三级梯队，任意一人不在岗都不影响项目运作。
4. 做了一堆服务，而且还做得挺好的样子，巅峰期的时候每个业务基本能用到的包括开发工具链都能在我们这 all in one，连开发环境都做到了 G 家 CodeShell 的水平。关注我的人知道年轻的时候我做过 Douban App Engine（DAE）大体如此。
5. 大概是全司唯一一个有着完善工具链和统一 workflow 的组织，DEV 在流程上做到完全自动化。完善的 QA，发布，培训和分享机制，结果导向，开心工作，放肆赚钱，我这 upper feedback 高分可不是空降来的。
6. 从 ROI 导向来看，基本上是最少的人干了最多的事，从不加班，WLB。最年轻的 P8 在他还不是 P8 的时候经常性请假就是「下一周打一周游戏」。
硬要说难过的话我只会为 SPP 团队难过，可惜了，即便我再找工作也不愿意带团队和组建团队了，过去的 2019.6-2021.6 相当开心，互相成就。我没有违背作为前豆瓣人在豆瓣学到的「做正确的事」，我也坚持了我的原则直到最后。

至于其他的工作比如拉起 Shopee Cloud 的大旗，虽然在 2020 年因为考虑其他老员工的心态悄咪咪的变成了 SPP Cloud，即便如此在我们自己做的大一统方案里面虚机服务，依然支持和服务了70 多个团队，还产出了 infra 整个部门唯一一篇过审专利等。

这些成就离不开 SPP 的成员们，我们证明了其实没有所谓的 cloud native 前提下依然可以 cloud，甚至可以在资源调度上成本（人力、机器）更低，效率更高，集群规模更大。Shopee 曾经是有机会做成大一统架构的，而这个机会就在 SPP，是你们把 SPP 这杠旗拉了起来。

同时我也感谢支持我们的 SG 团队，比如友军 HR 团队在坡县这个环境下帮我们捞人，比如既生瑜何生亮的 STO 团队提供的 SRE 支持，还有我们的客户爸爸们，过去 4 年希望你们满意。

我还感谢 SG 雷老板对我和我团队的支持，虽然一开始也有不信任过，但19年桌子一掀后他确实给了他能力范围内最大的支持，钱，人，技术，落地等。在他支持下，我能在这家市值曾经最高差不多 200B USD 的公司无限接近了 Infra Builder 所追求的大一统平台愿景，我很感谢他。

同时也感谢历史的车轮，在阶级轮动车门焊上的最后空隙送了我一个躺平大礼包（你看我就不会把这种事当做我个人的奋斗，至于谁会么……）。

2019.6-2021.6 真的很开心……

最后回答昨天一个朋友问我直击灵魂的问题，那就是现在的虾皮还值得来么，我说你都叫虾皮不叫 Shopee 了，你说呢？我只能说二级市场的股票它不香吗……

就酱。