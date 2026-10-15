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


# Roadmap

High priority:

[] Automatically store/read user habit heat map data
[] Scroll through months
[] Some way for user to input (click on a cell and input value)

Low priority:
[] Color changing
[] Light/dark mode

