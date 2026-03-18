from __future__ import annotations

from ig_splitter import create_app

app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
