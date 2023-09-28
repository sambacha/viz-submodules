# `viz-submodules`

Generate dependency graph (a naive one) in DOT notation. 

> Inspired by https://github.com/jrfonseca/xdot.py but without the GUI

## Setup

```bash
pyenv shell 3.10
```

```bash
poetry install
```

### Generate DOT Graph

```bash
python3 main.py $HOME/mevETH2 -m dot
```


![](./assets/example.svg)

## License

UPL-1.0
