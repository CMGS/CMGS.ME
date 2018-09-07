# gevent: the Good, the Bad, the Ugly

- category: life
- date: 2011-11-01
- tags: python, gevent

这是一篇翻译的文章，原文见：http://code.mixpanel.com/gevent-the-good-the-bad-the-ugly/

--------------

这是一篇翻译的文章，原文见[http://code.mixpanel.com/gevent-the-good-the-bad-the-ugly/](http://code.mixpanel.com/gevent-the-good-the-bad-the-ugly/)

转载的话麻烦加入原文和译者信息，谢谢。

第一次翻译难免有各种不足，感谢[Pig-soldier](http://pig-soldier.net/)友情帮助（虽然只贡献了一句话），还有淫杰（XXX字幕组的牛逼）的修正。

以此翻译纪念新项目的启动。

gevent: the Good, the Bad, the Ugly

Gevent: 优点，缺点，以及不优美的地方

I’m not going to spend much time describing what gevent is. I think the one sentence overview from its web site does a better job than I could:

我不想用很多时间去描述Gevent是什么，我想它官网上的一句总结足矣：

“gevent is a coroutine-based Python networking library that uses greenlet to provide a high-level synchronous API on top of libevent event loop.”

“Gevent是一种基于协程的Python网络库，它用到Greenlet提供的，封装了libevent事件循环的高层同步API。”

What follows are my experiences using gevent for an internal project here at Mixpanel. I even whipped up some performance numbers specifically for this post!

接下来我将阐述在Mixpanel中一个内部项目使用Gevent的经验。 为了这篇文章我还动手写了几个性能小测试。(Whipped up这里的意思让我迷惑哎- -）

##The Good
##优点

The main draw of gevent is obviously performance, especially when compared with traditional threading solutions.

首先Gevent最明显的特征就是它惊人的性能，尤其是当与传统线程解决方案对比的时候。

At this point, it’s pretty much common knowledge that past a certain level of concurrency doing I/O asynchronously vastly outperforms synchronous I/O in separate threads.

在这一点上，当负载超过一定程度的时候，异步I/O的性能会大大的优于基于独立线程的同步I/O这几乎是常识了。

What gevent adds is a programming interface that looks very much like traditional threaded programming, but underneath does asynchronous I/O.

同时Gevent提供了看上去非常像传统的基于线程模型编程的接口，但是在隐藏在下面做的是异步I/O。

Even better, it does all of this transparently.

更妙的是，它使得这一切透明。（此处意思是你可以不用关心其如何实现，Gevent会自动帮你转换）

You can continue to use normal python modules like urllib2 to make HTTP requests and they’ll use gevent instead of the normal blocking socket operations.

你可以继续使用这些普通的Python模块，比如用urllib2去处理HTTP请求，它会用Gevent替换那些普通的阻塞的Socket操作。

There are some caveats, but I’ll get back to those later.

当然也有一些需要注意的问题，我稍后会阐述。

For now, here’s the kind of performance improvement you can expect:
接下来，见证性能奇迹的时候到了。

<center>![alt](http://farm6.static.flickr.com/5133/5534035187_4a0af91dc9_b.jpg 图1)</center>

Thoughts

从上图看出

Ignoring everything else, gevent outperforms a threaded solution (in this case paste), by a factor of 4.

忽略其他因素，Gevent性能是线程方案的4倍左右（在这个测试中对比的是Paste，译者注：这是Python另一个基于线程的网络库）

The number of errors rises linearly with the number of concurrent connections in the threaded solution (these were all connection timeouts. I could probably have increased the timeout interval, but from a user perspective extremely long waits are just as bad as failures).

在线程方案中，错误数随着并发连接数的增长线性上升（这些错误都是超时，我完全可以增加超时限制，但是从用户的角度来看漫长的等待和失败其实是一个妈生的）。

gevent has no errors until 10,000 simultaneous connections, or at least until somewhere north of 5,000 simultaneous connections.

Gevent则是直到10,000个并发连接的时候都没有任何错误，或者说能处理至少5,000并发连接。

The actual requests completed per second were remarkably stable in both cases, at least until gevent fell apart in the 10,000 simultaneous connections test. I actually found this somewhat surprising. I initially guessed that requests per second would degrade at least a little bit as concurrency went up.

在这2种情况下，每秒实际完成的请求数都非常的稳定，至少直到Gevent在10,000个并发连接测试崩溃之前是如此。这一点让我感到非常的惊讶。我原本猜想的是RPS（每秒完成请求数）会随着并发的增多而下降。

The 10,000 simultaneous connections threaded test failed completely. I could have probably gotten this to work (seemed like something that some more ulimit tweaking could have solved), but I was mostly doing the test for fun so I didn’t spend any time on it.

线程模型在10,000并发连接测试中完全失败。我完全可以让它正常的工作（比如用一些资源优化技巧应该能做到），不过我纯粹是出于玩蛋来做这个测试的，所以没有在这上面花太多功夫。

If this kind of thing interests you, we’re hiring. (Yeah, I just intermingled content and advertising.)

如果这类东西能勾引起你的兴趣，我们正在招聘，你懂的。（没错，我就在内容里面混点广告宣传下。）

###Methodology

###测试方法

Here’s the python code I used for both tests:

这是我用来测试的Python代码:

```python
#!/usr/bin/env python

import sys

def serve_page(env, start_response):
    paragraph = '''
        Lorem ipsum dolor sit amet,
        consectetur adipisicing elit,
        sed do eiusmod tempor incididunt ut labore et
        dolore magna aliqua. Ut enim adminim veniam,
        quis nostrud exercitation ullamco laboris nisi ut aliquip
        ex ea commodo consequat.
        Duis aute irure dolor in reprehenderit in
        voluptate velit esse cillum dolore eu fugiat nulla pariatur.
        Excepteur sint occaecat cupidatat non proident,
        sunt in culpa qui officia deserunt mollit anim id est laborum.
    '''
    page = '''
        \
            \
                \Static Page\
            \
            \
                \
Static Content\
                %s
            \
        \
    ''' % (paragraph * 10,)

    start_response('200 OK', [('Content-Type', 'text/html')])
    return [page]

if __name__ == '__main__':
    def usage():
        print 'usage:', sys.argv[0], 'gevent|threaded CONCURRENCY'
        sys.exit(1)

    if len(sys.argv) != 3
        or sys.argv[1] not in ['gevent', 'threaded']:
        usage()

    try:
        concurrency = int(sys.argv[2])
    except ValueError:
        usage()

    if sys.argv[1] == 'gevent':
        from gevent import wsgi
        wsgi.WSGIServer(
            ('127.0.0.1', 10001),
            serve_page,
            log=None,
            spawn=concurrency
        ).serve_forever()
    else:
        from paste import httpserver
        httpserver.serve(
            serve_page,
            host='127.0.0.1',
            port='10001',
            use_threadpool=True,
            threadpool_workers=concurrency
        )
```

For the client, I used Apache bench with the following options:

在客户端，我在下面这些参数下使用Apache Bench:

-c NUM: where NUM is the number of simultaneous connections. This matched the number used on the server command line in each test.

-c NUM: 这里的NUM是并发连接数。在每一个测试中这个数与服务器命令行中使用的那个数是匹配的。（译者注：这里指脚本运行时需要提供的第二个参数）

-n 100000: all tests were over 100,000 requests. In the graph above, errors are not a rate, but rather the actual number of failed requests out of 100,000.

-n 100000: 所有的测试都需要完成100,000个请求。在上面的图中，错误率并没有统计，而是实际100,000请求中失败的请求数。

-r: continue even if there is a failure.

-r: 如果请求失败，自动重试

All tests were done with both client and server running on the same low-end, 512MB Rackspace Cloud VPS.

所有的测试包括服务端和客户端都是运行在一个低配置并且只有512MB内存的VPS上。

I initially thought I would need some way to limit the threaded solution to one CPU, but it turns out even though there are “four” cores on the VPS, you’re limited to 100% of one core. Not impressed.

我最初以为我需要用一些方法来限制线程方案到一个CPU上，但事实证明就算这VPS号称是“四核”，你也就只能让一个核心到100%。就是这么蛋疼。

###Linux tweaks for load testing
###负载测试中所做的Linux优化

I ran into a whole host of issues getting Linux working past ~500 connections per second.

当Linux处理超过500连接每秒的时候我遇到了一大堆的问题。

Almost all of these are related to all the connections being between the same two IP addresses (127.0.0.1 <-> 127.0.0.1).

基本上这些问题都是因为所有连接都是从一个IP到另一个相同的IP（127.0.0.1 <-> 127.0.0.1）。

In other words, you probably wouldn’t see any of these problems in production, but almost certainly would in a test environment (except maybe if you’re running behind a single proxy).

换句话说，你可能在生产环境中不会遇到这些问题，但几乎可以肯定的是这些问题一定会出现在测试环境中（除非你在后端跑一个单向代理）。

####Increase the client port range
####增加客户端端口范围

> echo -e ’1024\t65535′ | sudo tee /proc/sys/net/ipv4/ip_local_port_range

This increases the number of available ports to use for client connections. You’ll run out of ports very quickly without this (they get stuck in TIME_WAIT).

这一步将会使得客户端的连接有更多的可用的端口。没有这个的话你会很快的用尽所有端口（然后连接就处于TIME_WAIT状态）。

####Enable TIME_WAIT recycling
####启用TIME_WAIT复用

> echo 1 | sudo tee /proc/sys/net/ipv4/tcp_tw_recycle

This helps with connections stuck in TIME_WAIT as well and is basically required past a certain number of connections per second at least if the IP address pair remains the same. There’s another option tcp_tw_reuse that is available as well, but I didn’t need to use it.

这也会优化停留在TIME_WAIT的连接，当然这种优化至少需要每秒含有同样IP对连接超过一定数量的时候才会起作用。同时另一个叫做tcp_tw_reuse的参数也能起到同样的作用，但我不需要用到它。

####Disable syncookies
####关闭同步标签

> echo 1 | sudo tee /proc/sys/net/ipv4/tcp_syncookies

If you see “possible SYN flooding on port 10001. Sending cookies.” in dmesg, you probably need to disable tcp_syncookies. Don’t do this on your production server, but for testing it doesn’t matter and it can cause connection resets.

当你看到”possible SYN flooding on port 10001. Sending cookies.”这种信息的时候，你可能需要关闭同步标签（tcp_syncookies）。在你生产环境的服务器上不要做这样的事情，这样做会导致连接重置，只是测试的话还是没问题的。

####Disable iptables if you’re using connection tracking
####如果用到了连接追踪，关闭iptables

You’ll quickly fill up the netfilter connection table. Alternatively, you try increasing /proc/sys/net/netfilter/nf_conntrack_max, but I think it’s easier just to disable the firewall while testing.

你将会很快的填满你netfiler表。当然咯，你可以尝试增加/proc/sys/net/netfilter/nf_conntrack_max中的数值，但是我想最简单的还是在测试的时候关闭防火墙更好吧。

####Raise open file descriptor limits
####提高文件描述符限制

At least on Ubuntu, the open files limit for normal users defaults to 4096. So, if you want to test with more than ~4000 simultaneous connections you need to bump this up. The easiest way is to add a line to /etc/security/limits.conf like “* hard nofile 16384″ and then run ulimit -n 16384 before running your tests.

至少在Ubuntu上，默认每一个普通用户的文件描述符限制数是4096。所以咯，如果你想测试超过4000并发连接的时候，你需要调高这个数值。最简单的方法就是你测试之前在/etc/security/limits.conf中增加一行类似于”* hard nofile 16384″的东西，然后运行ulimit -n 16384这条shell命令。

##The Bad
##缺点

It can’t be all good, right? Right. Actually, most of the problems I had with gevent could be solved with better, more thorough documentation, which leads me to:

当然所有的事情不会这么好对吧？没错。事实上，如果有更完整的文档的话，很多我在用Gevent的问题会被解决得更好。（译者对于这类句子毫无抵抗力，凑合着看吧╮(╯_╰)╭）

###Documentation
###文档

Simply put: it’s not good. I probably read more gevent source code than I did gevent documentation (and it was more useful!). The best documentation is actually in the examples directory in the source tree. If you have a question, look there first — seriously. I also spent more time googling through mailing list archives than I like to.

简单的说，这货一般般。我大概读了比文档更多的Gevent源码（这样很有用！）。事实上最好的文档就是源码目录下的那些示例代码。如果你有问题，认真的瞄瞄看它们先。同时我也花了很多时间用Google去搜索邮件列表的存单。

###Incompatibilities
###兼容性

I’m specifically talking about eventlet here. In retrospect, this makes sense, but it can lead to some baffling failures. We had some MongoDB client code that was using eventlet. It simply didn’t work from the server process I was working on using gevent.

这里我特别想提到eventlet。回想起来，这是有一定道理的，它会导致一些匪夷所思的故障。我们用了一些eventlet在MongoDB客户端（译者注：一种高性能文档型数据库）代码上。当我使用Gevent的时候，它根本不能在服务器上运行。

###Order matters. Ugh.
###呃，使用顺序错误

Daemonize before you import gevent or at least before you call monkey.patch_all(). I didn’t look into this deeply, but what I gathered from a mailing list post or two is that gevent modifies a socket in python internals. When you daemonize, all open file descriptors are closed, so in children, the socket will be recreated in its unmodified form, which of course doesn’t work right with gevent. Gevent should handle this type of thing or at least provide a daemonize function that is compatible.

在你导入Gevent或者说至少在你调用Monkey.path_all()之前启动监听进程。我不知道为什么，但这是我从邮件列表中学到的，另一点则是Gevent修改了Python内部Socket的实现。当你启动一个监听进程，所有已经打开的文件描述符会被关闭，因此在子进程中，Socket会以未修改过的形式重新创建出来，当然啦，这就会运行异常。Gevent需要处理这类的异常，或者说至少提供一个兼容的守护进程函数。

###Monkey patching. Sometimes?
###Monkey Pathing，抽风咩？

So, most operations are patched by executing monkey.patch_all(). I’m not a huge fan of doing this sort of thing, but it is nice that normal python modules continue to function. Bizarrely, though, not everything is patched. I spent a while trying to figure out why signals weren’t working until I found gevent.signal. If you’re going to patch some functions, why not patch them all?

这么说吧，当你执行monkey.path_all()的时候，很多操作会被打上补丁修改掉。我不是很好这口，但是这样使得普通Python模块能够很好的继续运行下去。奇怪的是，这丫的不是所有的东西都打上了这种补丁。我瞄了很久想去找出为毛的Signals模块不能运行，直到我发现是Gevent.signal的问题。如果你想给函数打补丁，为毛的不全部打上咩？

The same applies to gevent.queue vs. standard python queue. Overall, it needs to be clearer (as in a simple list) when you need to use gevent specific API’s versus standard modules/classes/functions.

这问题同样适用于Gevent.queue与标准的Python queue模块。总之，当你需要用到Gevent特定的API去替换标准模块/类/函数的时候，它需要更清晰（就像简单的list一样）。

##The Ugly

##不优美的地方

gevent has no built in support for multiprocessing. This is much more a deployment issue than anything else, but it does mean that to fully utilize multiple cores, you’re going to need to run multiple daemon processes on multiple ports. Then, most likely, you’re going to need to run something like nginx (at least if you’re serving HTTP requests) to distribute requests among the server processes.

Gevent不能支持多进程。这是比其他问题更加蛋疼的部署问题， 这意味着如果你要完全用到多核，你需要在多个端口上运行多个监听进程。然后捏，你可能需要运行类似于Nginx的东西去在这些服务监听进程中分发请求（如果你服务需要处理HTTP请求的话）。

Really, the lack of multiprocessing capability just means another abstraction layer on your server that you might have added anyway for availability.

说真的，多进程能力的缺乏意味着为了使用中可用你又要在服务器上多加上一层东西。（译者注：真蛋疼的句子，不就是多一层Nginx或者HA么）

It’s a bigger issue when using gevent for client load testing. I ended up implementing a multiprocess load client that used shared memory to aggregate and print statistics. It was a lot more work than it should have been. (If anyone’s doing something similar, ping me and I can send the shell of the client program.)

在使用Gevent客户端负载测试中，这真是一个大问题。我最终是实现了一个使用共享内存的多进程负载的客户端去统计以及打印状态。这需花费更多的工作量在上面。（如果有人需要做同样的事情，联系我，我会给你这个客户端脚本程序）

##Last Words
##最后

If you’ve gotten this far, you noticed that I spent two full sections on negative aspects of gevent. Don’t let that fool you though. I’m convinced that gevent is a great solution for high performance python networking. There are problems, but mostly they’re problems with documentation, which will only improve with time.

如果你已经看到这里，你会发现我用了2个章节去阐述Gevent的缺点。不要被这些东西蒙蔽了你的眼睛。我相信Gevent对于Python网络编程来说是一种很伟大的解决方案。诚然它有各种各样的问题，但是大多数问题也仅仅是文档的缺失罢了，撑死了多用点时间嘛。

We’re using gevent internally. In fact, our server is so efficient that we’ll easily run out of bandwidth resources before computing resources (both processors and memory) for the VPS size we’re using.

我们内部正在使用Gevent。事实上我们的服务非常的高效，以至于在我们所用的那种规格的VPS上，很容易在用光计算资源（包括CPU和内存）之前用光带宽资源。
