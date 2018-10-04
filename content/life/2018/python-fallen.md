# 这破 Python

- date: 2018-10-4 7:52
- tags: python,work
- category: life

-------------------

没想到我一个 07 年就入坑 [CPyUG](https://groups.google.com/forum/#!forum/python-cn) 从此走上从业道路的人，也会有来吐槽 Python 的一天。事实上自从上一次 Guido van Rossum 因为 [PEP 572](https://www.python.org/dev/peps/pep-0572/) 事件而[长文](https://www.mail-archive.com/python-committers@python.org/msg05628.html)退出管理之后，我就想吐槽了。尤其是这个 Python 3.7 啊，你把 [async](https://docs.python.org/3/whatsnew/3.7.html) 改为保留字就算了，为啥作为属性还能报错，搞得基于 pylama 的静态检查在 3.7 下全部异常，真不知道管理层脑子里面都在想啥。

工程选择上前有狼后有虎，排头的 JAVA / C / CPP 系只要自己不作，基本是干不赢的。要知道即便是人力成本贼高的「精通 C/CPP 」从业人员，就能产出的东西而言比招一个玩 Python 玩得 6 的高到不知道哪里去了，更何况 JAVA 狗遍地走，人力成本你拿头去比啊。后面 Go 这种比你复杂不了多少，一个静态强类型语言工程管理成本大幅降低，最不济的人家至少不会去争 tab 还是 space 对吧。重写就有性能数量级的提升，还容易部署，开发运维都开心。

再看看 Python 这十几年都干了啥。10年前后 CPython 2 性能还能压着 Ruby 打，和 PHP 干得有来有回。现在一看 [Performance](https://benchmarksgame-team.pages.debian.net/benchmarksgame/faster/ruby.html)，连 Ruby 都能跳到 Python 头上踩一脚了，别提 [Pypy](https://pypy.org/) ，根本就上不了生产。11年的时候国内本来用 Python 的就少，我在金山做性能方面调研的时候算国内很早接触了 [Gevent](http://www.gevent.org/)/[fapws3](https://github.com/william-os4y/fapws3)/[uwsgi](https://uwsgi-docs.readthedocs.io/en/latest/) 的人，做了几次测试，写了几篇文章，翻译了几个报告，感觉这些东西真鸡儿棒，整个社区在这方面百花齐放，尤其是 Gevent。后来自己用 Gevent 实操了快盘的改造，又来到豆瓣以它为底层构建了 Douban App Engine，在 Python 2 的时代实现了全异步 IO 的应用框架，用过的开发都是爽得不要不要的。

然后喵的又过了 6 年再看，都他妈 Python 3.7 了，大清都亡了百来年了，算上 [tornado](https://www.tornadoweb.org/en/stable/) 这种显式 Promise/Future 的框架，能在生产中能弄起来的还是那么几样东西：Gevent，tornado，[greenify](https://github.com/douban/greenify) 和 flask/django 然后用 [gunicorn](https://gunicorn.org/) 跑。

[Asyncio](https://docs.python.org/3/library/asyncio.html)？是，标准库这个内置异步 IO 看起来香，吃起来是真的臭。好歹 Gevent 这类遇到 C level 的 IO 处理还有 greenify 这样的生产上验证过的库来 monkey patch 达到自动异步，各种生产的轮子也都有了，实在觉得隐式异步不好 debug 还有 tornado。一旦你用 Asyncio 就得自己重新实现一整套轮子。远的不说，MySQL 的 asyncio 异步轮子就没见着一个比 [MySQLdb](https://pypi.org/project/MySQL-python/) 完备度高的，看看 [aiomysql](https://github.com/aio-libs/aiomysql) 的 [issues](https://github.com/aio-libs/aiomysql/issues)，惨不忍睹，抄啥不好抄 [Pymsql](https://github.com/PyMySQL/PyMySQL)。还有那对标 [requests](https://github.com/requests/requests) 的 [aiohttp](https://aiohttp.readthedocs.io/en/stable/)，都出来多久了，还能有[这种](https://www.zhihu.com/question/266094857/answer/304655007)坑，拿头跟 requests 比啊？

[Sanic](https://github.com/huge-success/sanic)？抱歉，真的就只是一个 demo 而已，和 [flask](http://flask.pocoo.org/) 就别比了。

最后轰轰烈烈的 Python 2 和 Python 3 之争，字符串编码问题是解决了，结果引入了更多类型需要开发自行处理。王炸 Asyncio 发展了这么就还是个半成品全靠人填。yield 搞了半天语法糖还是不如隔壁 lua 的 coroutine，所以升个级最大的 feature 就是 print 成了函数么？

这么久的 2 to 3，性能上被曾经脚下的 Ruby 骑在了头上，痛点 GIL 反正是不会碰的，一辈子也不会碰的，杀手级特性在工业上落地就要堆人，语言层面上也没见着一个更加简练高效的语法。GC 优化？不存在的，就当没这个 GC，然后 PEP 就过家家一样争要不要新的语法糖？

喵喵喵？

看看当年 PEP 333 意气风发，再看看如今 PEP 572 眼界狭隘，这 Python 啊吃枣药丸。
