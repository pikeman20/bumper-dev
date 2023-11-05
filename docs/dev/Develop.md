# Developing

To start developing and contributing, install in dev mode.

```sh
$python3 -m venv venv
$source ./venv/bin/activate

$python3 -m pip install -r requirements.txt
$python3 -m pip install -r requirements-dev.txt
```

Review the [How It Works](How_It_Works.md) doc to understand the basics and then dive into the code.

As features and functions are added, be sure to add tests to keep the test coverage high.

## Testing

Bumper uses pytest for the majority of test cases, review current tests in the /tests directory.

### Running tests

**Run tests**

```sh
$python -m pytest tests
```

**Run tests with coverage**

```sh
$python -m pytest --cov=./ tests
```

**Run tests with coverage html report**

The report will be output into tests/report/index.html for further analysis.

```sh
$python -m pytest --cov=./ tests --cov-report html:tests/report
```
