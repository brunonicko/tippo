from invoke import task  # type: ignore  # noqa


@task
def conform(c):
    c.run("isort tippo tests ./docs/source/conf.py setup.py tasks.py -m 3 -l 88 --up --tc --lbt 0")
    c.run("black tippo --line-length=120")
    c.run("black tests --line-length=120")
    c.run("black setup.py --line-length=120")
    c.run("black tasks.py --line-length=120")


@task
def lint(c):
    c.run("isort tippo tests ./docs/source/conf.py setup.py tasks.py -m 3 -l 88 --up --tc --lbt 0 --check-only")
    c.run("black tippo --line-length=120 --check")
    c.run("black tests --line-length=120 --check")
    c.run("black setup.py --line-length=120 --check")
    c.run("black tasks.py --line-length=120 --check")

    c.run("flake8 tippo --count --select=E9,F63,F7,F82 --show-source --statistics")
    c.run("flake8 tests --count --select=E9,F63,F7,F82 --show-source --statistics")
    c.run("flake8 tippo --count --ignore=F811,F405,F403,F401,E203,E731,C901,W503 --max-line-length=120 --statistics")
    c.run("flake8 tests --count --ignore=F811,F405,F403,F401,E203,E731,C901,W503 --max-line-length=120 --statistics")


@task
def mypy(c):
    c.run("mypy tippo")


@task
def tests(c):
    c.run("python -m pytest -vv -rs tests")
    c.run("python -m pytest --doctest-modules -vv -rs README.rst")


@task
def docs(c):
    c.run("sphinx-build -M html ./docs/source ./docs/build")


@task
def checks(c):
    conform(c)
    lint(c)
    mypy(c)
    tests(c)
    docs(c)
