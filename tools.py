from datetime import date, datetime, timedelta, timezone

def get_season():
    current_year = datetime.now().year
    september_first = date(current_year, 9, 1)
    days_to_add = (7 - september_first.weekday()) % 7
    labor_day = september_first + timedelta(days=days_to_add)
    end_of_week_1 = labor_day + timedelta(days=3)
    today_est = datetime.now(timezone(timedelta(hours=-5))).date()
    if today_est>end_of_week_1:
        return current_year
    else:
        return current_year-1
    
def get_abbreviations():
    team_abbreviations = {
        "ARI": "Cardinals",
        "ATL": "Falcons",
        "BAL": "Ravens",
        "BUF": "Bills",
        "CAR": "Panthers",
        "CHI": "Bears",
        "CIN": "Bengals",
        "CLE": "Browns",
        "DAL": "Cowboys",
        "DEN": "Broncos",
        "DET": "Lions",
        "GB": "Packers",
        "HOU": "Texans",
        "IND": "Colts",
        "JAC": "Jaguars",
        "KC": "Chiefs",
        "LA": "Rams",
        "LAC": "Chargers",
        "LAR": "Rams",
        "LV": "Raiders",
        "MIA": "Dolphins",
        "MIN": "Vikings",
        "NE": "Patriots",
        "NO": "Saints",
        "NYG": "Giants",
        "NYJ": "Jets",
        "OAK": "Raiders",
        "PHI": "Eagles",
        "PIT": "Steelers",
        "SD": "Chargers",
        "SEA": "Seahawks",
        "SF": "49ers",
        "STL": "Rams",
        "TB": "Buccaneers",
        "TEN": "Titans",
        "WAS": "Commanders"
    }
    return team_abbreviations

def get_relevant_columns():
    relevant_columns = [
        "player_display_name",
        "position",
        "rushing_yards",
        "rushing_tds",
        "receptions",
        "targets",
        "receiving_yards",
        "receiving_tds",
        "tgt_sh",#target share
        "ry_sh",#receiving yards shares
        "wopr_y",#Weighted Opportunity Rating = 1.5 * Target Share + 0.7 * Share of Team Air Yards
        "rtd_sh",#receiving touchdowns share
        "yptmpa",#Receiving Yards Per Team Pass Attempt
        "fantasy_points_ppr"
    ]
    return relevant_columns

def format_team(team):
    return team[:len(team) // 2]

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