import requests

q = "what is the fire evacuation procedure?"

# Check if there's already a cached response
import redis
r = redis.Redis(decode_responses=True)
key = f"cache:query:{q.lower().strip()}"
cached = r.get(key)
print(f"Redis key exists: {cached is not None}")

# Make a query
resp = requests.post("http://localhost:8000/api/v1/query", json={"query": q})
d = resp.json()
print(f"Query result: cache={d['cache_status']}  confidence={d.get('confidence')}  time={d['response_time_ms']:.0f}ms")

# Check if it was stored now
cached_after = r.get(key)
print(f"Redis key exists after query: {cached_after is not None}")
if cached_after:
    print("SUCCESS: Response was stored in Redis cache!")
    # Now hit again to confirm HIT
    resp2 = requests.post("http://localhost:8000/api/v1/query", json={"query": q})
    d2 = resp2.json()
    print(f"2nd call: cache={d2['cache_status']}  time={d2['response_time_ms']:.0f}ms")
