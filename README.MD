## A simple Recommender System
This is a simpla recommender system to predict the movie rating.

The implemnted algorithms are `nearest neighbors`, `slope one` and `hybrid algorithm`.

PS: `slope one` has a poor performance, I don't come up with a good idea to determine the similarity between movie.

### Requirments
- Python3

### Usage
- Download and extract [ml-1m.zip](http://files.grouplens.org/datasets/movielens/ml-1m.zip) in the repo folder
- `pip3 install -r requirements.txt`
- `python3 conver_to_sqlite3.py`
- `python3 recommender.py`

- `analysis.py` is a simple script to check the RMSD for each algorithm.
- `result.txt` is a sample output


### Screenshot
![screenshot](https://raw.githubusercontent.com/bebound/recommender/master/Screenshot/1.png)
