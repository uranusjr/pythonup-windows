These are not actually executables, just placeholders to make the link
commands (e.g. "use" and "link") work during development without needing to
compile the shims.

The "shims_dir" key in "installation.json" point here. It will be overwritten
by the installer in real deployment to point to the real shims.
