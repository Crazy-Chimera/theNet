"""Deployment entry point for theNet."""

from __future__ import annotations

from thenet.server import serve


def main() -> None:
    serve()


if __name__ == "__main__":
    main()
