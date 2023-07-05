# CacheCloud Part II: The Basic Proxy

- date: 2023-07-06 10:49
- tags: work,redis,dev,project
- category: life

-------------------

A typical client request to Redis Cluster is depicted in the diagram below:

<center>![alt request](/media/cachecloud-part-ii-the-proxy/reqresp.png "MOVE")</center>

As you can see, the complexity of requesting Redis Cluster lies in handling the `MOVE` response. Without a proxy, the client handles it, which may result in lower overhead but requires a higher level of client implementation. In a proxy-based architecture, we need to consider the two fundamental aspects:

1. Command Parsing and Fast Forwarding
2. Ensuring Up-to-Date Routing and Slot Information

In our CacheCloud implementation, we conducted extensive comparisons of various parser solutions and found that [hiredis](https://github.com/redis/hiredis), which is also utilized by `Redis` itself, emerged as the optimal parser for Redis commands. Another advantage of choosing hiredis is that if there are any changes in the definition of commands at the future version, there is no need to maintain and update the command parser to accommodate these changes. 

When it comes to forwarding commands as fast as possible, using the pipeline mode is a reasonable choice. The pipeline mode allows for sacrificing latency in exchange for throughput. By bundling multiple commands together and sending them in a batch, the pipeline mode reduces the overhead of round-trip communication and improves overall command execution efficiency. 

By those, we parse commands, calculate slot information similar to Redis, and directly send them to the correct instances in most cases. But there are still something we have to deal with.

The fisrt on is how to handle blocking commands, such as `BLPOP`. How should we handle these commands to ensure optimal performance and prevent potential block?

A simple solution is to spawn a separate connection exclusively for such commands. These types of commands are typically fewer in number compared to simple commands like `SET` `GET`. Therefore, the additional overhead of establishing a dedicated connection for these commands is acceptable and helps mitigate any potential blocking issues.

The second thing is the handling of `MGET/MSET` commands, which are unique and popular among customers. Optimizing these commands in a clustered environment presents challenges. However, we will not delve into the specifics in this section. In the next section, we will provide an in-depth exploration of this topic, addressing the complexities and offering detailed insights.

In real world, the code just like:

```
pipeline = redis_client.pipeline()
for command in not_block_commands:
    pipeline.execute_command(*command)
    responses = pipeline.execute()
return responses
```

With this simple proxy, the complexities of Redis Cluster are hidden, allowing your clients to easily use it just like standalone Redis. Everything seems perfect until instances fail, master-slave switching occurs, another node initiates slot migration or whatever. Then your inbox is flooded with alerting emails and the error rate starts to rise.

Then you realized that you have to ensure the accuracy of routing and slot infomation.

Continuing with our CacheCloud, when the command parsed by the `hiredis`, normally it will be calculated and forward direct to the correct backend instance. However, if a slot has been migrated (resulting in a `MOVE` response), the proxy updates the routing table to reflect the new slot information.

At the same time, the proxy will send `cluster nodes` to one of the backend periodically to ensure that all information remains up to date. By querying the Redis Cluster nodes regularly, the proxy can refresh its routing and slot information and maintain the accuracy of the routing table.

From then on, no matter what happens in the cluster, the proxy can accurately and efficiently forward the corresponding basic command to the correct backend Redis instance. 

In the upcoming section, we will delve into another two important aspects:

1. Explore the networking, balance connections and traffic.
2. Optimizing the `MGET/MSET` as I mentioned before.
 
These two aspects will determine whether your implemented proxy is merely a toy or truly production-ready.