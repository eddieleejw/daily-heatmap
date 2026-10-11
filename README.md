# daily-heatmap
Habit tracking heatmap


# Installation

```
uv sync --locked
```

# Running


```
uv run python src/heatmap/api/app.py
```

# Docker

```
docker build -t heatmap .
```

```
docker run --rm -p 8000:8800 heatmap
```