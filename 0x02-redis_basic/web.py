#!/usr/bin/env python3
import requests
import redis
import functools

# Connect to the Redis server
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

# Decorator to implement caching and tracking
def cached_and_tracked(expiration=10):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(url):
            cache_key = f"cache:{url}"
            count_key = f"count:{url}"
            
            # Check if the result is already cached
            cached_result = redis_client.get(cache_key)
            if cached_result:
                # Increment the access count
                redis_client.incr(count_key)
                return cached_result.decode('utf-8')
            
            # Fetch the page content
            response = requests.get(url)
            if response.status_code == 200:
                content = response.text
                # Cache the result with an expiration time
                redis_client.setex(cache_key, expiration, content)
                # Increment the access count
                redis_client.incr(count_key)
                return content
            else:
                return f"Error: Unable to fetch page from {url}"
        
        return wrapper
    return decorator

# Apply the decorator to the get_page function
@cached_and_tracked(expiration=10)
def get_page(url: str) -> str:
    return requests.get(url).text

# Test the get_page function
if __name__ == '__main__':
    slow_url = "http://slowwly.robertomurray.co.uk/delay/10000/url/http://example.com"
    print(get_page(slow_url))
