from __future__ import annotations

from .app import create_app


def main() -> None:
    create_app()()


if __name__ == "__main__":
    main()