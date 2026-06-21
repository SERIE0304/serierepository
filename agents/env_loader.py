import os

def _load():
    if os.environ.get('ANTHROPIC_API_KEY'):
        return
    for path in [os.path.expanduser('~/.env'), os.path.expanduser('~/lodgers/.env')]:
        if not os.path.exists(path):
            continue
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"\''))
        break

_load()
