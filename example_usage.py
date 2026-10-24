"""Example usage for GenPark Fencing Token Distributed Lock.
100% Python Standard Library.
"""

from client import DistributedLockFencingToken

def main():
    lock = DistributedLockFencingToken()
    
    # Agent 1 acquires lock
    res1 = lock.acquire("agent_primary", ttl_seconds=5.0)
    print("Agent Primary acquired:", res1)
    
    # Downstream storage validates token
    token = res1["fencing_token"]
    is_valid = lock.validate_action(token)
    print(f"Downstream storage check (token={token}): Valid={is_valid}")
    
    # Agent 2 tries to acquire before expiry
    res2 = lock.acquire("agent_secondary", ttl_seconds=5.0)
    print("Agent Secondary attempt:", res2)
    
    # Primary finishes work and releases
    lock.release("agent_primary", token)
    
    # Secondary now acquires and receives strictly higher token
    res2_retry = lock.acquire("agent_secondary", ttl_seconds=5.0)
    print("Agent Secondary second attempt:", res2_retry)

if __name__ == "__main__":
    main()
