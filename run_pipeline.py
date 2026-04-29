import logging
import subprocess
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

STEPS = [
    ("Ingest",    "scripts/ingest.py"),
    ("Validate",  "scripts/validate.py"),
    ("Transform", "scripts/transform.py"),
    ("Export",    "scripts/export.py"),
]


def run_step(name: str, script: str) -> None:
    log.info("Starting step: %s (%s)", name, script)
    result = subprocess.run(
        [sys.executable, script],
        capture_output=True,
        text=True,
    )
    if result.stdout.strip():
        for line in result.stdout.strip().splitlines():
            log.info("[%s] %s", name, line)
    if result.returncode != 0:
        for line in result.stderr.strip().splitlines():
            log.error("[%s] %s", name, line)
        raise RuntimeError(
            f"Step '{name}' failed (exit code {result.returncode}):\n{result.stderr.strip()}"
        )
    log.info("Completed step: %s", name)


def main() -> None:
    log.info("Pipeline starting — %d steps", len(STEPS))
    for name, script in STEPS:
        if not Path(script).exists():
            log.error("Script not found: %s", script)
            sys.exit(1)
        try:
            run_step(name, script)
        except RuntimeError as exc:
            log.error("Pipeline aborted at step '%s': %s", name, exc)
            sys.exit(1)
    log.info("Pipeline finished successfully.")


if __name__ == "__main__":
    main()
