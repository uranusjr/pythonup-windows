import os

import invoke


SHIMSDIR = os.path.dirname(os.path.abspath(__file__))


@invoke.task()
def build(ctx, release=False, verbose=False):
    build_params = [
        '--release' * release,
        '--verbose' * verbose,
    ]
    with ctx.cd(SHIMSDIR):
        ctx.run('cargo build {}'.format(' '.join(build_params)))


@invoke.task()
def clean(ctx):
    with ctx.cd(SHIMSDIR):
        ctx.run('cargo clean')


@invoke.task()
def test(ctx):
    with ctx.cd(SHIMSDIR):
        ctx.run('cargo test')
