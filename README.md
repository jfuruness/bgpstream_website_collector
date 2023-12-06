[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3100/)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
![Tests](https://github.com/jfuruness/bgpstream_website_collector/actions/workflows/tests.yml/badge.svg)

# bgpstream\_website\_collector

* [Description](#package-description)
* [Usage](#usage)
* [Installation](#installation)
* [Testing](#testing)
* [Credits](#credits)
* [History](#history)
* [Development/Contributing](#developmentcontributing)
* [Licence](#license)


## Package Description

This package downloads information from bgpstream.com and stores it in a CSV

As a caveat, I wrote this a very long time ago when I was still an undergrad.
I've cleaned it up a bit, but this has a long way to go before it's good code quality
PRs welcome.
Also, almost everything is type ignored because mypy spazzes out with bs4
Also, the tests could really use a good update

## Usage
* [bgpstream\_website\_collector](#bgpstream\_website\_collector)

from a script:

```python
from pathlib import Path
from typing import Any

from bgpstream_website_collector import BGPStreamWebsiteCollector


def main():
    # Leave csv_path as None to not write CSV
    csv_path: Path = Path.home() / "Desktop" / "bgpstream_website.csv"
    rows: list[dict[str, Any]] = BGPStreamWebsiteCollector(csv_path=csv_path).run()


if __name__ == "__main__":
    main()
```

From the command line:

```
bgpstream_website_collector
```

## Installation
* [bgpstream\_website\_collector](#bgpstream\_website\_collector)

Install python and pip if you have not already.

Then run:

```bash
pip3 install pip --upgrade
pip3 install wheel
```

For production:

```bash
pip3 install bgpstream_website_collector
```

This will install the package and all of it's python dependencies.

If you want to install the project for development:
```bash
git clone https://github.com/jfuruness/bgpstream_website_collector.git
cd bgpstream_website_collector
pip3 install -e .[test]
pre-commit install
```

To test the development package: [Testing](#testing)


## Testing
* [bgpstream\_website\_collector](#bgpstream\_website\_collector)

To test the package after installation:

```
cd bgpstream_website_collector
pytest bgpstream_website_collector
ruff bgpstream_website_collector
black bgpstream_website_collector
mypy bgpstream_website_collector
```

If you want to run it across multiple environments, and have python 3.10 and 3.11 installed:

```
cd bgpstream_website_collector
tox
```

## Credits
* [bgpstream\_website\_collector](#bgpstream\_website\_collector)

Huge contributions to original version in lib_bgp_data to the testing from Tony Zheng

## History
* [bgpstream\_website\_collector](#bgpstream\_website\_collector)

1.1.2 Fixed event date bug
1.1.1 Fixed start_time -> start_date type
1.1.0 Added option to pass None to csv_path
1.0.0 First major release

## Development/Contributing
* [bgpstream\_website\_collector](#bgpstream\_website\_collector)

1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Test it
5. Run tox
6. Commit your changes: `git commit -am 'Add some feature'`
7. Push to the branch: `git push origin my-new-feature`
8. Ensure github actions are passing tests
9. Email me at jfuruness@gmail.com if it's been a while and I haven't seen it

## License
* [bgpstream\_website\_collector](#bgpstream\_website\_collector)

BSD License (see license file)
