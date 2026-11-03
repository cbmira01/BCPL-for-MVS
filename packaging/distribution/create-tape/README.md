# Create tape

Producer-side source for AWS tape creation and validation.

- `jcl/`: MVS jobs for unloading distribution datasets to tape.
- `scripts/`: host-side orchestration and manifest-driven job generation.
- `tests/`: tape structure and read-back verification.

This side may use the project development environment (WSL, Python, Hercules, `dspal`). Writing tape or executing JES jobs requires explicit separate approval. No implementation is present yet.
