import structlog
from support_api.utils import timed

structlog.configure()

@timed()
def compute(n: int) -> int:
    """Sum 0...n-1"""
    return sum(range(n))

print(f"compute result: {compute(1_000_000)}")

@timed(label="big-compute")
def compute_big(n: int) -> int:
    """Sum 0...n-1"""
    return sum(range(n))

print(f"compute_big result: {compute_big(1_000_000)}")