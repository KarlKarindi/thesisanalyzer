import datetime
import random


class Cache:

    def __init__(self):
        self.cache = {}
        self.max_cache_size = 10

    def contains(self, key):
        return key in self.cache

    def update(self, key, value):
        if key not in self.cache and len(self.cache) >= self.max_cache_size:
            self.remove_oldest()
        self.cache[key] = {"time_added": datetime.datetime.now(),
                           "value": value}

    def get(self, key):
        if self.contains(key):
            return self.cache[key]["value"]
        return None

    def remove_oldest(self):
        oldest_entry = None
        for key in self.cache:
            if oldest_entry is None:
                oldest_entry = key
            elif self.cache[key]["time_added"] < self.cache[oldest_entry][
                    "time_added"]:
                oldest_entry = key
        self.cache.pop(oldest_entry)

    @property
    def size(self):
        return len(self.cache)
