from __future__ import annotations

import argparse

from training.cli import add_training_args, print_summary
from training.pipeline import run_lightgbm_training


def main() -> None:
    parser = argparse.ArgumentParser(description="Train the LightGBM revenue model.")
    add_training_args(parser)
    args = parser.parse_args()
    try:
        payload = run_lightgbm_training(
            data_path=args.data_path,
            output_dir=args.output_dir,
            valid_size=args.valid_size,
            random_state=args.random_state,
        )
    except ImportError as exc:
        raise SystemExit(f"Dependency error: {exc}") from exc
    print_summary(payload)


if __name__ == "__main__":
    main()
