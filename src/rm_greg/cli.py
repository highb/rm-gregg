"""Command-line interface for rm-greg."""

from __future__ import annotations

import argparse
import sys


def main(argv: list[str] | None = None) -> int:
    """Entry point for the rm-greg CLI."""
    parser = argparse.ArgumentParser(
        prog="rm-greg",
        description="Gregg Shorthand learning system for reMarkable tablets",
    )
    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Extract command
    extract_parser = subparsers.add_parser("extract", help="Extract stroke data from .rm files")
    extract_parser.add_argument("input", help="Path to .rm file or directory")
    extract_parser.add_argument("-o", "--output", help="Output path (JSON or Parquet)")
    extract_parser.add_argument(
        "--format",
        choices=["json", "parquet"],
        default="json",
        help="Output format",
    )

    # Synthetic command
    synth_parser = subparsers.add_parser("synthetic", help="Generate synthetic training data")
    synth_parser.add_argument(
        "--unit", type=int, default=1, help="Curriculum unit number"
    )
    synth_parser.add_argument(
        "--count", type=int, default=100, help="Samples per primitive"
    )
    synth_parser.add_argument("-o", "--output", required=True, help="Output directory")

    # Train command
    train_parser = subparsers.add_parser("train", help="Train a stroke classifier")
    train_parser.add_argument("data", help="Path to training data directory")
    train_parser.add_argument("--unit", type=int, default=1, help="Curriculum unit")
    train_parser.add_argument(
        "--model",
        choices=["rf", "svm", "lstm", "cnn"],
        default="rf",
        help="Model architecture",
    )
    train_parser.add_argument("-o", "--output", required=True, help="Model output path")

    # Evaluate command
    eval_parser = subparsers.add_parser("evaluate", help="Evaluate a practice session")
    eval_parser.add_argument("input", help="Path to .rm file")
    eval_parser.add_argument("--model", required=True, help="Path to trained model")
    eval_parser.add_argument("--unit", type=int, default=1, help="Curriculum unit")

    # Serve command
    serve_parser = subparsers.add_parser("serve", help="Start the API server")
    serve_parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    serve_parser.add_argument("--port", type=int, default=8000, help="Port to listen on")
    serve_parser.add_argument("--model", help="Path to trained model")

    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    # Dispatch to subcommands (to be implemented)
    print(f"Command '{args.command}' is not yet implemented.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
