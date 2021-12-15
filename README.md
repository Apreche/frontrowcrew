# betafrontrowcrew

[![GitHub Super-Linter](https://github.com/Apreche/betafrontrowcrew/workflows/Lint%20Code%20Base/badge.svg)](https://github.com/marketplace/actions/super-linter)

This is the source code for the site [beta.frontrowcrew.com](https://beta.frontrowcrew.com). At some point it will be swapped over to [frontrowcrew.com](http://frontrowcrew.com).

## Local Development

To perform development tasks on this project there are a few possible dev environment setups possible. More may be added in the future.

### Linux

If coding in a plain old *nix environment, working on this project is not too difficult. First, make sure that a Python 3.8+ interpreter is installed and working. Make sure that [poetry](https://python-poetry.org/) has been installed using that Python interpreter. Then change to the directory where the project exists and run `poetry install`.

That's it. The project should be ready to roll using an sqlite database locally. To enable the dev server or perform other Django tasks use commands such as

```Python
poetry run python manage.py runserver
```

To make life a little bit easier, there is a script in `bin/manage` that can be used as follows:

```shell
./bin/manage runserver
```

### VSCode

This repository contains a [remote dev container](https://code.visualstudio.com/blogs/2020/07/01/containers-wsl) Docker configuration for VSCode.

To use this setup, first install [Docker Desktop](https://www.docker.com/products/docker-desktop), [WSL2](https://docs.microsoft.com/en-us/windows/wsl/install), and [VSCode](https://code.visualstudio.com/).

Once all those things are installed, simply opening this project in VSCode should automatically bring up some prompts to install any required VSCode extensions.

Now there should be three options available under "Run and Debug". The first option will launch the django local development server. The second will execute the Django test framework. The third option will perform database migrations.

That's all there is to it. Just start coding and use the three options as necessary.

## CI/CD

This project is configured using [Djangogoboot](https://github.com/apreche/djangogoboot). This means it has a complete CI/CD pipeline powered by GitHub actions.

For the most part, developers don't have to think about it since it is already setup and working. Just submit all new work as a pull request to the main branch, and the rest will take care of itself. There are, however, just a few things to be aware of.

### Linting

One of the configured CI steps is [GitHub Super-Linter](https://github.com/github/super-linter). Any pull request must pass the linter without error, or it will not be merged. It is highly recommended to run the Linter locally and fix all errors before submitting or updating a pull request. To do so, there is a handy script. This script requires docker to be setup and working properly.

```shell
./bin/lint
```

### Testing

The django tests will be run on every pull request. If any tests fail, the pull request will not be merged. If a pull request contains new Python/Django code that is not covered by at least minimal testing, it will not be merged.

### Deployment

Because we are still in the beta/development phase of the project, all pull requests that are merged into the main branch will immediately and automatically be deployed to [beta.frontrowcrew.com](https://beta.frontrowcrew.com). Once the project is live on frontrowcrew.com, this may change such that deployments only occurr when a new tagged release is created.
