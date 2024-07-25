# Site Response
This program gathers http and https responses from websites and IPs.

## Installation
1. Clone the repository with `git clone repo_url` or download the zip file and extract it.
2. Install [Python3](https://www.python.org/downloads/)
3. Install the required libraries by running the following command:
```bash
$ pip install -r requirements.txt
```

### Installation Problems
1. If `pip` is not recognized, use `pip3` instead.
2. If neither works, use `py -m pip install -r requirements.txt`, `python -m pip install -r requirements.txt`, or `python3 -m pip install -r requirements.txt`.
3. If nothing works, follow the instructions on the [official website](https://pip.pypa.io/en/stable/installation/).

## Usage
Run the program with the following command:
```bash
$ py site_response.py -f <filename> | -u <url> | -ip <ip range> [-t <timeout> -r <retries> -b <batch size>]
```

If `py` is not recognized, use `python` or `python3` instead.

### Examples
```bash
$ py site_response.py -f urls.txt -t 2 -r 3
$ py site_response.py -u https://www.google.com
$ py site_response.py -ip 192.168.1.0/24
$ py site_response.py -f sites.txt -b 300
```