# frontrowcrew

[![GitHub Super-Linter](https://github.com/Apreche/frontrowcrew/workflows/Lint%20Code%20Base/badge.svg)](https://github.com/marketplace/actions/super-linter)

This is the source code for the site [frontrowcrew.com](https://frontrowcrew.com).

## Local Development

The architecture of this site is not too complex, but is comprised of quite a few components. The officially supported local development setup involves using [Docker](https://www.docker.com/), [VSCode](https://code.visualstudio.com/), and [Development Containers](https://containers.dev/).

If you would like to work on this site with a different environment, then take a look inside the `.devcontainer` directory. Try your best to replicate the environment defined therein using the tools you prefer.

### VSCode

If you wish to use VSCode as suggested, development on this project is very easy. First, make sure that Docker is installed and functioning. Then install the [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension in VSCode.

Once those are installed, open this project in VSCode. A prompt will appear asking if you would like to reopen the project in a container. Say yes. If the prompt does not appear you can go to the command palette and choose the option `Dev Containers: Rebuild and Reopen in Container`.

Once the container is successfully built, you are ready to get to work. The integrated VSCode terminal will automatically have the Python environment activated. That is the primary means of working with the project. [pgcli](https://www.pgcli.com/) is pre-configured. If you run it from the terminal, it will be automatically connected to the development database.

There are also two predefined launch profiles for the VSCode debugger. One of them will run a local web server. The other will run all of the Django unit tests.

## CI/CD

This project is configured using [Djangogoboot](https://github.com/apreche/djangogoboot). This means it has a complete CI/CD pipeline powered by GitHub actions.

For the most part, developers don't have to think about it since it is already setup and working. Just submit all new work as a pull request to the main branch, and the rest will take care of itself. All code is tested and linted before it is merged. Any code that is merged is automatically deployed.

### Linting

One of the configured CI steps is [GitHub Super-Linter](https://github.com/github/super-linter). Any pull request must pass the linter without error, or it will not be merged. It is highly recommended to incorporate equivalent linters into your programming environment to avoid a hassle.

The default VSCode dev container configuration automatically enables an extension to use the [Ruff](https://github.com/astral-sh/ruff) Python linter. This guaratees that at least all the Python code is compliant.

### Testing

The django tests will be run on every pull request. If any tests fail, the pull request will not be merged. Bugfix patches should always have at least one test to guard against regression. New features should have at least a few basic tests to ensure they at least don't crash horribly.