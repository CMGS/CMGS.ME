# 掉入神坑爬不起来了

- date: 2015-9-15 11:52
- tags: docker,work
- category: life

-------------------

没有大漩涡的日子脸一直都很黑，别人家的暗黑3 2小时远古毕业，我家的暗黑三巅峰300才凑齐一套套装还不能战撸T10，工作上遇到神坑简直是日了狗了……

##### docker [go-dockerclient](https://github.com/fsouza/go-dockerclient) 的问题。

在用 attach 接口的时候，本来是一个 established 的 HTTP 1.1 长连接，库的 hijack 实现会关闭到 docker daemon 的连接，然后卡着不释放，通过 FIN_WAIT2 状态传递数据……虽然我不知道这种方法有啥问题，但是每次 lsof 一堆 FIN_WAIT2 状态的连接感觉还是怪怪的，相比之下官方的 [docker-py](https://github.com/docker/docker-py) 实现就没这个问题，稳定的 established 连接赏心悦目。

##### 还是 docker go-dockerclient 库的问题。

一开始小六子发现他家实现的 stats 接口会有很严重的 goroutine 泄露问题，给打了个补丁[「肥六的PR」](https://github.com/fsouza/go-dockerclient/pull/346/files)，然而过了1个多月后突然再次出现严重的泄露。一开始我发现是编译机的环境被 checkout 了，库版本并没包含这个补丁，然后更新到了最新的 go-dockerclient，没想到这才是噩梦的开始。

接下来的半个小时，agent 的 goroutine 已经达到了400多个，一晚之后这个值是 3000+。通过 pprof 发现大多数都卡在了 /usr/local/go/src/net/http/transport.go L976 这里。没办法再去翻了下 go-dockerclient 的源码，发现是9月9日一位新加坡华人引入的 [buffer reading](https://github.com/fsouza/go-dockerclient/commit/edc2bd38d8fa79581371ea78b3c09935877a1ade) 导致的。以前 go-dockerclient 对 http response body 的处理是直接读取所有的内容，这位华人觉得比较浪费内存就实现了一个 buffer reader 。然而对于我们这种用非 stream 模式调用 stats 接口的来说，每30秒一次的调用可能使得 response body 的 size 横跨 2个 buffer，而后面的这个 buffer 有时候会填不满，然后就傻逼了。

好在周六这位巴西的 auther 果断的 revert 前一个提交并通过新的 PR记录下来，重编译一波后故障解除。老实讲这点内存也废不了多少啊……

##### docker daemon exec 负担太重的问题。

在早期 docker 版本中， exec 是不会被 daemon track 的，意味着对 exec 的操作虽然会打乱 container 的进程树，但对 daemon 的负担并不是很大，有点像 API 版的 nsenter。1.6 还是 1.7 之后 docker daemon 开始 track exec 起来，以前那种 create run 的方式会造成一大堆的 exec instance 并且和容器 bind 在一次，inspect 的那画面美得不能看，并且我看了 docker 源码似乎会对长时间不用 exec instance 做 gc。

所以我们一开始改为了 create store run 这种方式，复用 exec。但经过漫长的线上踩坑之后，发现一旦机器容器数量过多，这种30秒一次的 exec 对 daemon 的负担还是比较高的，因此没事有事的 timeout 就家常便饭了。于是我们换成了外部调用 nsenter 来做类似的事情。

##### race condition

换完 nsenter 之后，golang 恰逢推出了可以自举的 1.5 版，我们也第一时间更新了编译机的编译环境，但这一次有点玩大了。

编译之后之前 agent 该怎么跑就还是怎么跑，于是我们更新了线上所有的机器。事实证明，周五不要乱更新这句话不是瞎比比啊。紧接着周六处理了 goroutine leak，这个时候感觉也没多大事，直到周日80% agent 相继 crash 才发现比起 go-dockerclient 的问题，golang 的这次升级问题更严重。（还好实现是旁路的……

一开始，crash 的日志类似于这样

```
panic: runtime error: invalid memory address or nil pointer dereference
[signal 0xb code=0x1 addr=0x6 pc=0x45e97a]

goroutine 64068 [running]:
github.com/HunanTV/eru-agent/app.(*EruApp).updateStats(0xc82015c2a0, 0x20002)
        /root/.go/src/github.com/HunanTV/eru-agent/app/metric.go:91 +0x81e
github.com/HunanTV/eru-agent/app.(*EruApp).Report.func1(0xc82015c2a0, 0xecd86aab7, 0xc821d08d25, 0xbecce0)
        /root/.go/src/github.com/HunanTV/eru-agent/app/metric.go:38 +0x30
created by github.com/HunanTV/eru-agent/app.(*EruApp).Report
        /root/.go/src/github.com/HunanTV/eru-agent/app/metric.go:49 +0x63d
```

这个 91 行的代码在[这里](https://github.com/HunanTV/eru-agent/blob/11507d69d202d68b14396803d474f66cc9404a05/app/metric.go#L91 )简直再正常不过了，foreach 一个 map，然后把内容赋值给另外一个 map，这……这不科学对吧。

然后我使用 print 大法，想把 network 和 Info 打印出来看看，写下了 fmt.Println(network, self.Info) 这种，临时编译了一个丢线上服务器，没过多久它果然崩了，而这次的 trackback 就更匪夷所思。

```
panic: runtime error: invalid memory address or nil pointer dereference
[signal 0xb code=0x1 addr=0xd0 pc=0x409d78]

goroutine 5349 [running]:
reflect.mapiterinit(0x7f78c0, 0xc8201b8c90, 0x15)
        /usr/local/go/src/runtime/hashmap.go:966 +0x4a
reflect.Value.MapKeys(0x7f78c0, 0xc8201b8c90, 0x15, 0x0, 0x0, 0x0)
        /usr/local/go/src/reflect/value.go:1068 +0xec
fmt.(*pp).printReflectValue(0xc8200700d0, 0x7f78c0, 0xc8201b8c90, 0x15, 0x76, 0x0, 0xa47800)
        /usr/local/go/src/fmt/print.go:893 +0x2500
fmt.(*pp).printArg(0xc8200700d0, 0x7f78c0, 0xc8201b8c90, 0x76, 0x0, 0x0)
        /usr/local/go/src/fmt/print.go:810 +0x53c
fmt.(*pp).doPrint(0xc8200700d0, 0xc820633a88, 0x2, 0x2, 0x101)
        /usr/local/go/src/fmt/print.go:1254 +0x258
fmt.Fprintln(0x7f94f3515358, 0xc820040010, 0xc820633a88, 0x2, 0x2, 0x2, 0x0, 0x0)
        /usr/local/go/src/fmt/print.go:254 +0x67
fmt.Println(0xc820633a88, 0x2, 0x2, 0x0, 0x0, 0x0)
        /usr/local/go/src/fmt/print.go:264 +0x73
github.com/HunanTV/eru-agent/app.(*EruApp).updateStats(0xc82048e1c0, 0xc8201b8bd0)
        /root/.go/src/github.com/HunanTV/eru-agent/app/metric.go:90 +0x847
```

是的，golang 自己的 print 实现都 crash 了！这根本不科学！！即便是给一个没初始化的 map 应该可以安全的 println 出来的！！我已经开始怀疑 golang 1.5 的实现是不是有点问题……然后周一的时候果断升级了 1.5.1 ，并且利用 golang 里面 map 默认传 ref 特性重构了一小部分代码，自以为没问题的情况下又丢了个临时编译的版本到线上……然而这并没有什么卵用，喜闻乐见的是这次它还是崩了，traceback 已经变成了这样

```
unexpected fault address 0x0
fatal error: fault
[signal 0xb code=0x80 addr=0x0 pc=0x45ec3d]

goroutine 1072 [running]:
runtime.throw(0x963b08, 0x5)
        /usr/local/go/src/runtime/panic.go:527 +0x90 fp=0xc8204698a0 sp=0xc820469888
runtime.sigpanic()
        /usr/local/go/src/runtime/sigpanic_unix.go:27 +0x2ab fp=0xc8204698f0 sp=0xc8204698a0
runtime.aeshashbody()
        /usr/local/go/src/runtime/asm_amd64.s:981 +0x38d fp=0xc8204698f8 sp=0xc8204698f0
runtime.mapassign1(0x7f7920, 0xc820122d80, 0xc820469a68, 0xc8204699f0)
        /usr/local/go/src/runtime/hashmap.go:424 +0xbf fp=0xc8204699a0 sp=0xc8204698f8
github.com/HunanTV/eru-agent/app.(*EruApp).updateStats(0xc820120b60, 0x7e1120, 0xc82054dee0)
        /root/.go/src/github.com/HunanTV/eru-agent/app/metric.go:94 +0x82b fp=0xc820469ea8 sp=0xc8204699a0
github.com/HunanTV/eru-agent/app.(*EruApp).Report.func1(0xc820120b60, 0xecd886826, 0xc8157384d9, 0xbecce0)
        /root/.go/src/github.com/HunanTV/eru-agent/app/metric.go:39 +0x30 fp=0xc820469f80 sp=0xc820469ea8
runtime.goexit()
        /usr/local/go/src/runtime/asm_amd64.s:1696 +0x1 fp=0xc820469f88 sp=0xc820469f80
created by github.com/HunanTV/eru-agent/app.(*EruApp).Report
        /root/.go/src/github.com/HunanTV/eru-agent/app/metric.go:51 +0x63d
```

这个 L94 就是这个L106。当时我已经开始叫小伙伴准备降级 golang 了，这种 unexpected fault 有时候9分钟就挂，有时候跑2天才挂，而且在本机很难复现，基本上不可能 debug，除非用二进制手段去做。抱着最后一丝希望，我问了问教授。教授沉默了好久，先说，唔这代码看上去是没问题，加个对 Info 这个 map 的 nil 判断 workaround 下。然后我加了发现 if 那句直接也是 unexpected fault，更倾向于是多路 gc 和默认 GOMAXPROCS 修改后引发的问题。接着教授说你看看 GetNetStats 这个函数是在 2个 goroutine 里面操作同一个 Map，以前的版本只是 thread unsafe，现在的会不会直接 panic，一下子我就感觉到可能就是这样。

早期的 GetNetStats 的实现就是 exec 的那个实现，当时扒了 go-dockerclient 的 example 代码这样一写也相安无事，因为 go 1.5 之前 gc 是单路的，GOMAXPROCS 默认也只是1核。虽然 map 在 golang 里面是 thread unsafe，但对于一个默认单核并且上下文相关的 map 做有序读写操作的时候，语义上和实际结果是可以保证的。官方也只是说 it's not defined what happens when you read and write to them simultaneously，而这里我们的代码并没并发读写同一个 map。换成 nsenter 之后其实这个 spawn 出去的 goroutine 已经完全没有存在的必要了，当时忘记删了也就使得处理逻辑上和之前的版本还是一样。

然而在 golang 1.5，多路并发 gc 和 GOMAXPROCS 默认值的修改，使得编译出来的 binary 天生具有跨核 spawn 的能力。CHANGELOG 出来之后我记得还看过业内有人讲 1.5 的 golang 标志着 goroutine 调度器的成熟（成熟个卵）。但这样一来，这种看上去安全的代码（语义上上下文相关，顺序读写）实际上变得不安全起来，随机 spawn 出来的 goroutine 保不齐会跨线程，在 24核的机器上这个概率就比较大了。一旦这里的 goroutine 和发起函数处于不同的线程，那么之前「安全」的语义就会变得不安全起来，然后引发 golang runtime 的错误。我推测是 goroutine 结束后，gc 又做了什么幺蛾子回收了这个跨线程 goroutine 的数据什么的，然后引发了真正调用这些数据的代码 panic。总之，这就是他妈一个坑啊！

所以这也暴露了几个问题，首先，不要瞎升级，有时候升级会带来很高的正向收益，但是这种大版本什么的还是得谨慎，是时候申请新的编译机了。再者，golang 对于 goroutine 的追踪和控制力度还是太弱，runtime goroutine 调度器调试和 debug 始终没有什么比较好的方法，全靠静态推断，相比之下 rust 这种一切都可以掌握的感觉还是好不少。比如说这次，goroutine 怎么 spawn ，spawn 去哪个线程处理什么的，对于上层开发者而言都是黑箱，加之连 print 都能 panic，随机 panic 时间等各种因素，如果不是教授看出这个地方虽然语义上没问题，但可能 unsafe，说不定我们就直接降级处理了。

anyway，要国庆了希望线上别特么再出幺蛾子了，open-falcon 的问题解决完之后就可以开开心心的去玩啦！
