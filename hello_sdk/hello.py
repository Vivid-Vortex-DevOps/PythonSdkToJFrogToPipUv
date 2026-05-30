def greet(name: str = "World") -> str:
    return f"Hello, {name}! — from hello-sdk v0.1.0"


def main() -> None:
    print(greet())
