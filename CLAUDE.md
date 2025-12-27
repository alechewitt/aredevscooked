Uses uv. Run tests like this:

uv run pytest

Commit early and often. Commits should bundle the test, implementation, and documentation changes together.

Run Black to format code before you commit:

uv run black .

## Style Guide
General:

1. Don't use comments to split up your files. The function/class names you use should be sufficiently descriptive to not require sections (e.g., # 1. Clean Data). If you find yourself wanting to do this, this is probably a sign you need split your file into multiple files. 

### Testing
When you are writing unit tests, please do not use classes. If you see you have states you need to keep track with, favor pytest fixtures