# Dynamically Load Balancer

- date: 2015-11-9 17:37
- tags: nginx,work,openresty
- category: life

-------------------

即便是我厂这样一掷千金随便空降CTO的土豪国企，也不是那么愿意花 $7000/y 就为了 5 个 Nginx plus instance。考虑我们自己的调度平台 Eru 承载的业务通用性和对类似于青云那种界面点 2 下就有一个 7 层 LB 的向往，我琢磨了下我这 10 年都没写 C 的水平（那天心血来潮写了个 launcher 已经被诚老师吐槽到死了），于是默默的上了地球上最大的同性交友网站上研究了几天。

对于 LB 而言，目前来说大多数都会选用 Nginx，但是这货的开源版本有个问题就是状态是随着 Nginx 走的。意味着如果对于 Server 的变动，需要有个「第三方」从外部发起一个 HUP 信号来使得 Nginx 可以在不中断请求处理的同时 reload configuration。

你看，这就意味着如果要做到 Nginx 社区版的更新配置首先需要更新本地配置文件，然后再由「第三方」发出 HUP 信号。考虑到 LB 往往可能不是一台，那么第一个需求就有导致「配置不一致」的风险，而第二个需求则使得强状态的 Nginx 没那么好做弹性扩容。

容器时代无状态短生命期的容器死活又是那么的频繁，虽然说 HUP 信号的 reload 从经验来看是一种相当可靠的做法，但还是可能因为频繁 reload 导致 old workers 过多的情况。另外在我厂这种没有 redarrow 进行并行远程执行命令工具又没有 puppet 保证配置同步的幺蛾子公司，想做 LB 扩容也是一件很麻烦同时也得小心翼翼的事。

现有的架构下我们只有一台 LB （恩网卡也有跑满风险），六子写的 reloader 通过 subscribe eru publish 出来的消息更新配置并发出 HUP 信号勉强的达到了我们的预期。考虑到新的南方机房集群下有多个 LB 的需求，于是就弄出了一个堪用的版本的 dynamically load balancer [eru-lb](https://github.com/HunanTV/eru-lb)。

eru-lb 是基于 [Openresty](http://openresty.org/) + [ngx_http_dyups_module](https://github.com/yzprofile/ngx_http_dyups_module) 写的，调研用了 5天，大概架子也就1下午搞定。这个过程中的一些选择主要就是下面这些东西了。

##### Openresty 和它的组件们

不得不说 Openresty 是个伟大的工具，双章可真是一人一把核武器唉，纯编程领域我这辈子基本达不到他们这高度了，当然我也不会去研究佛经。在这个项目调研过程中我首先看了下它能对 upstream 操控的组件，也就是 [lua-resty-upstream-module](https://github.com/openresty/lua-upstream-nginx-module)，原始状态下它只能 readonly 已有配置中的 upstreams，SINA 的小伙伴提供的 PR 里面已经有 production 级别的增删改，但还是只能增对已有的静态 upstream 配置进行操作。

另外这个模块最最最蛋疼的一点在于单次修改仅针对于当前 worker 生效，如果要同步得利用 init worker 时候的自定义 sync timer cycle，而恰恰这个 cycle 不是那么好写。利用锁来同步进程间数据的话，你得考虑「高频配置更新请求」的条件下 worker upstream 的数据一致性，毕竟容器的生生灭灭是一件「高频次」的活。这其中包括：

a. 在前一个 sync 请求还没完成的情况下如何保证后一个 sync 请求不会覆盖共享数据空间，也就是处理 sync 请求的原子性和一致性需求。
b. 如果利用外部存储，比如 redis，通过 pubsub 来达到「带着请求」的锁这么一个目的，那么如何保证与外部存储之间的可靠性。毕竟无论是 tcp 还是 udp，这种操作的可靠性风险还是挺大的，一旦出错一来没那么好 debug，二来会导致配置的不一致。

最后因为没法对一个 upstream 本身进行动态的增删查改（此模块仅仅针对于 server/peer 这一级），因此我放弃单纯利用此模块来开发 DLB。

##### Nginx 1.9 upstream 新特性 [zone](http://nginx.org/en/docs/http/ngx_http_upstream_module.html#zone) 配合 [ngx_dynamic_upstream](https://github.com/cubicdaiya/ngx_dynamic_upstream) 模块

zone 特性其实可以看成是官方给 worker 之间开辟了一个贡献的数据空间来共享 upstream 配置。Nginx plus 提供了另外一个 [ngx_http_upstream_conf_module](http://nginx.org/en/docs/http/ngx_http_upstream_conf_module.html) 来提供 server/peer 一级的动态增删查改，某个小伙子就抄了一发实现了这个 ngx_dynamic_upstream 模块来提供同样的功能。

但可惜的是，此模块依然只适合已有的静态 upstream 中 server/peer 的修改，没法做到单独增加一 upstream 断来满足我们的需求。在 Openresty 没放出 balancer_by_lua 特性前我一度想以此方案作为最终解决方案，采用叠加镜像的方法一个 server 对应一个「定制化」的 LB，虽然麻烦了点但也能用。结果下午刚完成 base image 的构建，晚上章大神就放出了众人期待已久的 balancer_by_lua 特性。

##### [balancer_by_lua](https://github.com/openresty/lua-nginx-module/blob/balancer-by-lua/t/133-balancer.t)，Openresty 最新特性，提供了在 Upstream 层自定义 balance 策略的可能

首先这个特性也只能针对已有的 upstream，另外从目前开放的 API 来看它提供的更多的是策略层面上支持（而且还不完善），比如只有用那个后端，重试几次等API，再引入外部存储来存后端配置和策略的话还会影响其效率。虽然它在其公司已经 production 很久，但我们这边最终放弃单独使用它来开发 DLB。

这个特性最大的用处就是实现比 round robin 比 ip hash 甚至比 fair 更好的 balance 策略，完全可以针对业务形态和实时状态来精确倒流，我觉得这在流量调度领域应该是相当之强大的一个特性了，个人推测在 Cloud Foundry 也是用在这个方面，说不定哪天还是会用到的。

##### ngx_http_dyups_module，又爱又恨的一个模块

我们之前尝试使用过一段时间，但对 upstream health check 的不兼容让我们最终放弃了它（虽然 health check 已经完全不需要 nginx 来做了）。在这一次的围观中我看到淘宝的 tengine 已经把齐 merge 进主干，那么意味着它其实已经是 production ready 的状态，故再度进入到了我们的考虑之中。

最关键的是，这货支持动态的生成一个「upstream」啊，而不仅仅是增删查改其中的 server/peer。早期让人担心的 health check 问题也已经解决，另外也支持 max_fails 和 timeout 等设置，当然 backup 属性还是会导致 500，但已经无关紧要了。

我花了大量的时间来读这个模块的代码（和 nginx 一起），原理上和用 Openresty timer cycle 同步 worker 配置差不多，一个 share mem 负责存着这些 upstreams，然后一个 C timer 来进行 sync。比起 Openresty 的实现，能针对 upstream 本身的操作就击中了我们最大的痛点了（而且不影响 http 1.1 的长连接）。但不得不吐槽的是这货的代码质量实在是……硬编码有点多啊，比如 api 要求一定就是 2 个 path 段什么的。我曾尝试着修改了一部分，后面发现其 lua API 返回竟然是走的状态码什么的，其实就是拿 http handler 那套包了个皮，并没做核心逻辑解耦的情况下我就懒得改了……妈蛋还要完整的看一遍 nginx API 再重新实现它这个季度 KPI 就完不成了好吧！

当然最后我们还是用这货来实现 upstream 本身和其配置的热配置，配合使用 Openresty 的 API 来满足动态的把 domain 和 upstream backend 联系起来，满足了我们这种变态的小需求。同时 nginx 和其配置的分离又使得我们可以让 DLB container 化，从而达到按需扩容缩容目的。另外我们还在其中加入了人见人爱的按照 domain 分析 upstream 响应状态，这回看业务还有什么话好说，Openresty 大法真心棒。至于日志什么的 errorlog 反正已经支持 stderr 的输出模式，而 accesslog 按 domain 分离什么的就交给 logstash 去做吧，最不济让业务自己记录也不是什么大问题嘛。

总之又能解放一部分「人力」的活了，CTO 要是看到的我要求不高啊，节省了10份人力的成本你给我4份就行，么么哒~~
