# Redis Cluster The Intro

- date: 2023-03-28 10:49
- tags: work,redis,dev,project
- category: life

-------------------

[Redis Cluster](https://redis.io/docs/reference/cluster-spec/) is an important feature introduced in Redis since version 3 to provide a way for Redis to operate in a distributed system. While the standalone version of Redis is a single-instance mode, Redis Cluster provides a solution to high availability and partitioning.

There are 3 major pros:

- By default, Redis Cluster has 16384(16k) slots, implements automatic partitioning, which means it divides the total available data across multiple Redis nodes. This process is also known as sharding. Sharding can greatly increase the storage capacity and processing power of your Redis database, because the data and load are spread across multiple machines. The distributed nature of Redis Cluster allows operations to continue even when a subset of the nodes are experiencing failures or are unreachable, enhancing the system's overall availability.

- As an event-driven system, redis is designed to utilize only a single CPU core when running. This inherent architecture can sometimes limit the performance of Redis, especially in multi-core CPU systems. With Redis Cluster, each instance running on a different CPU core. This effectively enables Redis to leverage the power of multi-core systems, overcoming the single-core limitation of a standalone Redis instance. In practical tests, as you increase the number of nodes in the Redis Cluster, the total processing power of the system increases correspondingly. 

- In a Redis Cluster, each node utilizes the 'gossip' protocol to maintain connections with all other nodes, enabling rapid and precise failure detection. Every node is responsible for a fraction of the total data, so a single node's failure results in a loss of only 1/n of the data. Through the master-slave mechanism, this potential loss is further mitigated.

At the same time, the cluster also has some cons:

- The gossip protocol of Redis Cluster results in additional bandwidth overhead. As the number of nodes in the cluster increases, this overhead becomes more significant. At the same time, the more instances there are, the greater the impact on the speed of the cluster's self-healing capabilities. We need to balance the number of nodes and plan for maximum capacity, maintaining a balance between the two. Generally, although Redis Cluster supports up to 16k nodes, it is not recommended to exceed 2k nodes (including master and slave nodes).

- Essentially, Redis does not implement full ACID properties. Therefore, for a cluster, transactionality and context-based commands are almost unusable, such as when executing Lua scripts. Therefore, the command set of Redis Cluster is a subset of standalone Redis. The usage mode should be decided based on the upper layer user's usage patterns.

- For certain data structures such as lists and hashes, it's easy for hot data to become concentrated on a few instances, leading to high resource utilization on these instances. It's necessary to modify the business operations to break up the hot data in order to achieve the goal of dispersing data and balancing hotspots.

Of course, the most significant issue with Redis Cluster adopting the gossip protocol is that it requires the `client` to be aware of the data distribution and instance situation (such as master-slave switching). As a result, the industry has divided into several approaches to address this issue:

- Some choose not to upgrade to Redis version 3, but instead modify the last version 2 (typically 2.6) with a traditional distributed system design. This involves creating a `meta` server to store data routing information and establishing a proxy related to it. The modified Redis simply stores the data. This approach allows for easy expansion of the number of Redis instances because without the `gossip` protocol, there is no bandwidth overhead. However, this solution is not officially supported, so we would have to maintain this `revised version` ourselves. The famous project in this way is [codis](https://github.com/CodisLabs/codis), The author of the project, who is also the creator of [TiDB](https://www.pingcap.com/), has designed both projects to have nearly identical architectures.

- Some people choose the native Redis Cluster implementation. However, in the earlier years (around 2015~2018), the biggest issue was the varying levels of support across different language SDKs, with Java's [Jedis](https://github.com/redis/jedis) being basically the only viable option. The biggest issue with this solution is maintaining consistency in the routing tables across multiple clients. If changes occur in the cluster, such as master-slave switching, the client side might see inconsistent cluster statuses due to various reasons, leading to an increase in error rates. Having said that, this solution, without intermediaries, indeed offers the best performance.

- The last approach involves placing a proxy in front of Redis Cluster to shield the complexity of cluster commands (such as handling MOVE instructions), making it appear to the client as if it's a 2.6 version of Redis. This method centralizes the complexity in proxies, which are fewer in number than Redis instances. This not only makes it easier to maintain consistency in maintaining routing table information, but also facilitates centralized optimization, such as balancing traffic or connections, and providing higher performance mset/mget command sets, etc.

Since 2014, I have consistently chosen the third approach. Why? Because I prefer to adhere to the KISS principle, keeping the architecture simple and straightforward. Here are a few publicly available proxy implementation projects for reference:

- [Redis-cerberus](https://github.com/projecteru/redis-cerberus), our first production ready proxy which was implemented in [mgtv](https://mgtv.com/) peroid by cpp verion 11. The father of this project is living in Japan happily ever after.
- [Redis-corvus](https://github.com/eleme/corvus), after we conducted a private sharing session at [Ele.me](https://www.ele.me/) company, they decided to use our architectural design as well. However, since they were not very familiar with CPP version 11 at the time, their engineer [maralla](https://github.com/maralla) chose to rewrite the entire proxy in C.
- [predixy](https://github.com/joyieldInc/predixy), maybe the fastest proxy opensourced in github, I didn't know the author.

We won't delve into the implementation details of these proxies or discuss some new proxy designs I've been involved with in previous work in this section. Generally speaking, although Redis Cluster is an official solution, its usage is significantly different from that of standalone Redis, with many noteworthy considerations. In the next section, I would like to share the trade-offs I made based on Redis Cluster in order to construct the 'largest caching system in Southeast Asia'.