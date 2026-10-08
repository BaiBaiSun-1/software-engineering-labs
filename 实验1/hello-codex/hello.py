"""A tiny program demonstrating a Codex generated first draft and refinement."""

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="输出一条 AI 编程问候语")
    parser.add_argument("--name", help="可选称呼，例如：同学")
    args = parser.parse_args()

    prefix = f"你好，{args.name}！" if args.name else ""
    print(f"{prefix}Hello, AI 编程！")


if __name__ == "__main__":
    main()
