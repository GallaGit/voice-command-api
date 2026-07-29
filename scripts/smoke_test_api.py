import json
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:8001"


def call(method: str, path: str, data: dict | None = None, timeout: float = 90.0):
    body = None if data is None else json.dumps(data).encode()
    headers = {"Content-Type": "application/json"} if data is not None else {}
    req = urllib.request.Request(BASE + path, data=body, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode()
            print(f"{method} {path} -> {resp.status} {raw}")
            return resp.status, json.loads(raw) if raw else None
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode()
        print(f"{method} {path} -> {exc.code} {raw}")
        return exc.code, raw


def main() -> None:
    call("GET", "/")
    call("GET", "/tasks")
    call("POST", "/tasks", {"title": "Buy milk"})
    call("POST", "/tasks", {"title": "Walk dog", "done": True})
    call("GET", "/tasks")
    call("PATCH", "/tasks/1", {"done": True})
    call("PUT", "/tasks/2", {"title": "Walk the dog", "done": False})
    call("DELETE", "/tasks/2")
    call("GET", "/tasks")
    print("--- instruction ---")
    call("POST", "/instruction", {"transcription": "add buy groceries to my list"})
    print("--- transcribe json ---")
    call("POST", "/transcribe", {"transcription": "add buy bread to my list"})
    call("GET", "/tasks")


if __name__ == "__main__":
    main()
