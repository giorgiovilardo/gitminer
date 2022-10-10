# gitminer

takes info from your org git repos and smarmells them

this project is basically private, but it's public because I have to share it. don't look at it.

## install and run

1. `pip install -r requirements.txt` in a 3.9 venv
2. `cp .env.dist .env` and fill the data 
3. `python gitminer.py`
4. `./thinger.sh` when told to

## depends on

we have some dependencies:

* `requests` and `python-dotenv` in the project
* some clis:
  * `jq`
  * `scc`

## roadmap

Probably add code-maat or some other churn measure tool
