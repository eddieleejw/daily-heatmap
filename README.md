# daily-heatmap
Habit tracking heatmap


# Installation

```
uv sync --locked
```

# Running


```
uv run python -m heatmap.api.app
```

# Docker

```
docker build -t heatmap .
```

```
docker run --rm -p 8000:8800 -v heatmap-data:/app/data heatmap
```


# Roadmap



- [x] Add new habit option
- [ ] "Zen mode" option
- [ ] Dark mode option
- [ ] Color gets gradually darker the longer the streak
- [ ] Streak (and settings)
- [x] Dropdown menu to select what habit the grid represents
- [x] Default date range (today - 6 months)
- [x] Automatically store/read user habit heat map data
- [x] Select start and end date
- [x] Some way for user to input (click on a cell and input value)
