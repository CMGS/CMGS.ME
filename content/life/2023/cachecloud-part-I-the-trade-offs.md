# CacheCloud Part I: The Trade-offs

- date: 2023-07-05 10:49
- tags: work,redis,dev,project
- category: life

-------------------

Indeed, every decision comes with trade-offs, and choosing Redis Cluster as a caching system is no exception. There was once a colleague at Didi, who was at the D11 level, said: 'Cache is just cache. Don't try to address persistence issues within a caching system.' Compared to building a caching system with tools like [Memcached](https://memcached.org/), the 'persistence' capability of Redis is quite appealing. Frankly my friend, everything has a cost. When it comes to constructing a robust caching system based on Redis Cluster, sacrificing this 'persistence' capability is one of the costs we must accept.

As we know, there are four ways in Redis for persistence:

1. Snapshot is the default method, but it can result in data loss if a system or instance failure occurs between two snapshots.
2. Append-only file (AOF) persistence with fsync strikes a balance between data reliability and performance. However, this method relies entirely on the operating system's timing for disk flushing, which still poses a risk of data loss. Additionally, an incomplete write to the AOF file can make it impossible to replay it entirely during instance restart, leading to failed restarts.
3. Append-only file persistence with a second interval guarantees a maximum data loss of one second.
4. Append-only file persistence by every operation theoretically provides the best data reliability but at the expense of performance. However, there is still a potential risk of incomplete data.

If we require persistence, regardless of the chosen mode, we need to consider disk pressure. The snapshot process, which involves concentrated write operations, can result in IO peaks. Additionally, continuous pressure on the disk can arise from AOF rewrites and other operations related to persistence. It is essential to carefully manage and monitor disk utilization to ensure optimal performance and prevent potential bottlenecks caused by excessive disk pressure.

So Why bother concerning ourselves with persistence? Let's leave it aside. After all, a cache system doesn't require any persistence, right? That's the first aspect I decided to forgo when developing CacheCloud.

Another visionary from Apple once said, 'Customers always don't know what they want, so don't give them choices.' It is true that Redis Cluster can support up to 16K instances. But, as mentioned before, when the number of instances increases to around 2K (including both master and slave nodes), the bandwidth usage of the gossip protocol cannot be ignored. Typically, standard servers in an IDC are configured with 24 to 32 core CPUs and two network cards with around 20G bandwidth each, using bond mode to connect to two TOR switches for high availability. With this configuration, each machine can handle approximately 22 to 30 instances. In scenarios where a large cluster is densely deployed, the bandwidth utilization tends to remain high. 

Especially when it comes to communication between the proxy and the instances of Redis Cluster, the pipeline mode is commonly used. This mode trades throughput for latency, and as a result, it puts additional pressure on the bandwidth itself. The increased throughput achieved by the pipeline mode may lead to higher bandwidth utilization, otentially reaching its limits and becoming a bottleneck.

Therefore, the second aspect to consider is determining the maximum configuration we can provide to users. This decision needs to be optimized based on the underlying server configurations. Additionally, balancing the overall availability and bandwidth overhead of Redis Cluster can be achieved by adjusting the node health check mechanism. This ensures a trade-off that maximizes both the system's availability and resource utilization.

When you reach this point, you may have two questions regarding the previous discussion:

1. Why is the maximum number of instances in Redis Cluster less than the total number of CPU cores?
2. Why hasn't memory usage been explicitly considered in the previous context?

Well, these are excellent questions that are directly related to the Redis Cluster replication mechanism. In short, the replication mechanism in Redis Cluster is similar to standalone Redis. Initially, the master node forks itself and takes a snapshot of its memory, storing it as a file in memory. This snapshot is then sent to the slave node during the 'full sync' process, which involves recording the offset to track replication progress. Once the slave fully applies the snapshot, it compares the offset and requests the Append-Only File (AOF) stream to catch up with the master ('partial sync'). If the offset difference is significant, it triggers another round of 'full sync', and this cycle repeats periodically.

Now, let's address the two questions raised:

The maximum number of instances being less than the total number of CPU cores is due to the need for optimal performance. Each Redis instance operates on a single thread and ideally should be assigned to a dedicated core. But the full sync process, other system processes and tasks also require CPU resources. Therefore, it's necessary to leave some cores available for those tasks, resulting in a lower number of Redis instances. In our CacheCloud, we assign around 1.01 CPU to a redis instance, I understand that you are curious about how to allocate 1.01 CPU, but that belongs to [Eru](https://github.com/projecteru2/core)'s story. 

When it comes to memory, more is not always better. While we can achieve a "huge memory capacity" in Redis Cluster by using a smaller number of instances with larger memory sizes, there is a performance limit for Redis instances that can only utilize a single CPU core. In a modern physical server without the pipeline mode, the maximum achievable throughput for a single CPU core is typically around 80K to 120K reads, depending on the typical dataset size for each operation (which is specific to your business requirements). This information helps determine the maximum manageable memory size.

In our CacheCloud, there are two values for the maximum memory size per instance. In most cases, it is 16GB, but there are special cases where it can be 32GB. It's important to note that we cannot use up all the system's memory. Some memory needs to be reserved for other tasks and system requirements. Additionally, we must consider the extra memory overhead caused by the Copy-On-Write (COW) mechanism during full sync process.

Honestly when designing and implementing CacheCloud, the trade-offs mentioned are just a small part of the overall picture. For example, asking customers to transform hash data into simple strings with prefix data is one approach. And it's important to note that Redis Cluster is also an eventually consistent system, and we cannot guarantee strong consistency for reads and writes. After all, solving the [CAP theorem](https://en.wikipedia.org/wiki/CAP_theorem) problem would require a significant effort. 

Can we do it? - Of course, we can.<br/>
Can we change it? - Sure, no problem.

But everything comes with a cost my friend. There is no universally applicable, perfect system. As I mentioned at the beginning, cache is cache, and that's the essence of it.