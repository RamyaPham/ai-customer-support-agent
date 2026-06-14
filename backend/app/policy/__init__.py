from pathlib import Path


def load_policy() -> str:
    policy_path = Path(__file__).parent / "refund_policy.md"
    return policy_path.read_text()
