import nfl_data_py as nfl
from tools import *
import json

current_season = get_season()

fantasy_positions = [
    "RB",
    "WR", 
    "TE"
]

relevant_columns = get_relevant_columns()

def add_to_schedule(data, teams, week):
    for index in range(0,2):
        current_team = teams[index]
        opposing_team = teams[1-index]
        if current_team not in data.keys():
            data[current_team] = ["BYE"]*18
        schedule = data[current_team]
        schedule[week-1] = opposing_team
        data[current_team]= schedule
    return data

def format_df(data, columns_to_keep):
    return data.loc[:, columns_to_keep]

def get_value(input_value):
    full_length = len(input_value)
    for index in range(1, len(input_value)):
        sub_string = input_value[0:index]
        reps = full_length/len(sub_string)
        if full_length%len(sub_string)==0:
            if input_value==sub_string*int(reps):
                return sub_string
    return input_value

def fix_typos(data, bad_columns):
    for column in bad_columns:
        data[column] = data[column].apply(get_value)
    return data

def get_teams_schedule(year=current_season):
    schedules =nfl.import_schedules([year])
    schedules = schedules[schedules['game_type'] == 'REG']
    team_schedules = {}
    for row in schedules.itertuples(index=False):
        home_team = row.home_team
        away_team = row.away_team
        week = row.week
        team_schedules = add_to_schedule(data=team_schedules, teams=[home_team, away_team], week=week)
    return team_schedules

def get_all_data(year=current_season):
    data = nfl.import_seasonal_data([year], "REG")
    data = format_df(data, relevant_columns)
    data = fix_typos(data, bad_columns=["player_display_name","position"])
    data = data[data['position'].isin(fantasy_positions)]
    return data

def get_all_names(year=current_season):
    names = get_all_data(year)
    names  = names.sort_values(by='fantasy_points_ppr', ascending=False)
    names = names.player_display_name.unique().tolist()
    return names

def get_player_stats(name, year=current_season):
    df = get_all_data(year)
    row = df[df["player_display_name"] == name]
    if not row.empty:
        row_dict = row.iloc[0].to_dict()
        del row_dict["player_display_name"]
        json_object = json.dumps(row_dict)
        return json_object
    else:
        return {}

def get_library_ids():
    ids_df = nfl.import_ids()
    columns = ['fantasypros_id', 'position']
    return format_df(ids_df, columns)