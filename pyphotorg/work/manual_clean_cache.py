import os

from hash_cache import DEFAULT_CACHE_PATH, HashCache

# ======================================
# Main
def main():
    """Clear the persistent deduplication hash cache."""
    cache_path = os.getenv("DEDUP_CACHE_PATH", DEFAULT_CACHE_PATH)

    # Display the cache path using the format of the other manual operations.
    print("=====================================")
    print("Launching manual cache clean operation ...")
    print('- cache-path={}'.format(cache_path))
    print("=====================================")

    # A missing cache is normal before the first deduplication run.
    if not os.path.exists(cache_path):
        print("... No cache found !")
    else:
        # Empty the cache while keeping the configured cache location intact.
        with HashCache(cache_path) as hash_cache:
            deleted_count = hash_cache.clear()
        print("... {} cached file hash(es) removed !".format(deleted_count))

    print("... Operation ended !")


if __name__ == "__main__":
    # execute only if run as a script
    main()
