# Fantasy Playbook

The purpose of this website is to bring together data from various sources and present it in a user-friendly manner that facilitates trend and pattern analysis.

## How to Use

Before running the website, ensure that all required libraries are installed:

```
pip install -r requirements.txt
```

Then, execute `main.py`:

```
python main.py
```

## Projections

The algorithms for generating projections are currently in the development phase. Here is an overview of the current algorithm's process:

1. Retrieve the player's position and their team's schedule.
2. Gather recent statistics on players' performance in the specified position against all opponents.
3. For each opponent in the schedule, calculate the z-score representing how well players perform against them.
4. Utilize the player's historical statistics to determine the mean and standard deviation of their fantasy points. Calculate a score corresponding to the z-score from the previous step.
5. Sum the scores for the remaining opponents in the current season to estimate the potential value a player could provide to your team.

Please note that this algorithm does not aim to provide exact point projections. Instead, it identifies players with high potential who might be undervalued. By considering factors such as schedule strength and performance volatility (standard deviation), it offers insights into players' potential contributions and value to a fantasy team.

## Sources of Data

Data sources utilized:

- [Fantasy Pros](https://www.fantasypros.com)
- [FFToday](https://www.fftoday.com/index.html)
- [NFL Data Py](https://github.com/cooperdff/nfl_data_py)

## Future of the Project

The ongoing plan involves continually adding new pages and features to the website. Your ideas, comments, and suggestions for enhancing this platform are greatly appreciated.