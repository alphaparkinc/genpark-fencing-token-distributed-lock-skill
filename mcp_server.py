"""MCP Server for GenPark Fencing Token Distributed Lock.
100% Python Standard Library.
"""

import json
import sys
from client import DistributedLockFencingToken

lock = DistributedLockFencingToken()

def handle_request(req):
    method = req.get("method")
    params = req.get("params", {})
    req_id = req.get("id")

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": "acquire_lock",
                        "description": "Acquire lock and receive a monotonically increasing fencing token",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "client_id": {"type": "string"},
                                "ttl_seconds": {"type": "number"}
                            },
                            "required": ["client_id"]
                        }
                    },
                    {
                        "name": "release_lock",
                        "description": "Release held lock with matching fencing token",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "client_id": {"type": "string"},
                                "fencing_token": {"type": "integer"}
                            },
                            "required": ["client_id", "fencing_token"]
                        }
                    },
                    {
                        "name": "validate_fence",
                        "description": "Verify that a downstream write request has the active valid fencing token",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "fencing_token": {"type": "integer"}
                            },
                            "required": ["fencing_token"]
                        }
                    }
                ]
            }
        }
    elif method == "tools/call":
        name = params.get("name")
        args = params.get("arguments", {})
        if name == "acquire_lock":
            cid = args.get("client_id", "")
            ttl = args.get("ttl_seconds", 10.0)
            res = lock.acquire(cid, ttl_seconds=ttl)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}
            }
        elif name == "release_lock":
            cid = args.get("client_id", "")
            tok = args.get("fencing_token", 0)
            ok = lock.release(cid, tok)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"content": [{"type": "text", "text": json.dumps({"released": ok})}]}
            }
        elif name == "validate_fence":
            tok = args.get("fencing_token", 0)
            valid = lock.validate_action(tok)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"content": [{"type": "text", "text": json.dumps({"valid": valid})}]}
            }

    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Method not found"}}

def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            res = handle_request(req)
            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()
        except Exception as e:
            err = {"jsonrpc": "2.0", "id": None, "error": {"code": -32000, "message": str(e)}}
            sys.stdout.write(json.dumps(err) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
