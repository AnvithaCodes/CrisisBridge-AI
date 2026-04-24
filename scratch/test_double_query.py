import requests

q = "is the elevator safe during fire?"
r1 = requests.post("http://localhost:8000/api/v1/query", json={"query": q}).json()
r2 = requests.post("http://localhost:8000/api/v1/query", json={"query": q}).json()

print(f"1st Query Status: {r1['cache_status']}")
print(f"2nd Query Status: {r2['cache_status']}")
