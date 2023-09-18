from nfl_data import get_library_ids
from bs4 import BeautifulSoup
import pandas as pd
from tools import *
import threading
import requests

current_season = get_season()

def fetch_from_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        return None
    
def get_fantasy_pros_ids():
    url = "https://www.fantasypros.com/nfl/adp/ppr-overall.php"
    html_content = fetch_from_url(url)
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find_all('table')[0]
    table_data = []
    rows = table.find_all('tr')
    for row in rows[1:]:
        column = row.find_all(['th', 'td'])[1]
        position = row.find_all(['th', 'td'])[2].get_text()[0:2]
        if position in ["RB","WR", "TE"]:
            hyperlinks = column.find_all('a')
            link_name = hyperlinks[0]['href'][13:-4]
            try:
                name = hyperlinks[1]['fp-player-name']
                id = hyperlinks[1]['class'][1][6:]
            except:
                name = hyperlinks[2]['fp-player-name']
                id = hyperlinks[2]['class'][1][6:]
            table_data.append(
                [
                    name,
                    link_name,
                    int(id)
                ]
            )
    fantasy_pros_df = pd.DataFrame(table_data, columns=["name", "link", 'fantasypros_id'])
    nfl_data_df = get_library_ids()
    merged_df = pd.merge(fantasy_pros_df, nfl_data_df, on='fantasypros_id', how='inner')
    merged_df = merged_df[['name', 'link', 'position']]
    return merged_df

fantasy_pros_ids = get_fantasy_pros_ids()

def get_fantasy_pros_names():
    return fantasy_pros_ids.name.unique().tolist()

def format_name(player):
    return str(fantasy_pros_ids[fantasy_pros_ids["name"]==player]['link'].iloc[0])
    
def get_position(player):
    return str(fantasy_pros_ids[fantasy_pros_ids["name"]==player]['position'].iloc[0])

def scrape_table(url, index=0):
    html_content = fetch_from_url(url)
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find_all('table')[index]
    table_data = []
    rows = table.find_all('tr')
    for row in rows:
        row_data = []
        columns = row.find_all(['th', 'td'])  
        for column in columns:
            value = column.get_text(strip=True)
            try:
                row_data.append(float(value))
            except:
                row_data.append(value)
        table_data.append(row_data)
    return table_data

def get_position_projections(position, week):
    position = position.lower()
    url = f"https://www.fantasypros.com/nfl/projections/{position}.php?week={week}&scoring=PPR"
    data = scrape_table(url)
    receiver = data[0][1]=="RECEIVING"
    if position not in ["k", "dst"]:
        data = data[1:]
    if position in ["rb", "wr"]:
        if receiver:
            data[0][2] = "REC YDS"
            data[0][3] = "REC TDS"
            data[0][5] = "RUSH YDS"
            data[0][6] = "RUSH TDS"
        else:
            data[0][2] = "RUSH YDS"
            data[0][3] = "RUSH TDS"
            data[0][5] = "REC YDS"
            data[0][6] = "REC TDS"
    df = pd.DataFrame(data[1:], columns=data[0])
    df["Player"] = df["Player"].apply(fantasy_pros_format)
    return df

def get_player_projection(player): 
    player = format_name(player)
    url=f"https://www.fantasypros.com/nfl/projections/{player}.php?scoring=PPR"
    data = scrape_table(url, index=0)
    return pd.DataFrame(data[1:], columns=data[0])

def get_player_weekly_stats(player, year=current_season):
    player = format_name(player)
    url = f"https://www.fantasypros.com/nfl/games/{player}.php?scoring=PPR&season={year}"
    data = scrape_table(url)
    receiver = data[0][1]=="Receiving"
    data = data[1:-1]
    for index in range(1, len(data)):
        data[index][0] = int(data[index][0].replace("Week ",""))
    data[0][0] = "Week"
    if receiver:
        data[0][5] = "rec yards"
        data[0][8] = "rec tds"
        data[0][10] = "rush yards"
        data[0][13] = "rush tds"
    else:
        data[0][4] = "rush yards"
        data[0][7] = "rush tds"
        data[0][10] = "rec yards"
        data[0][13] = "rec tds"
    data = [item for item in data if item[1] != 'BYE Week']
    data = [item for item in data if item[3] != '-']
    df = pd.DataFrame(data[1:], columns=data[0])
    return df.sort_values(by="Week")

def get_points_against(position, year=current_season):
    position = (["QB", "RB", "WR", "TE"].index(position.upper())+1)*10
    url = f"https://www.fftoday.com/stats/fantasystats.php?Season={year}&GameWeek=Season&PosID={position}&Side=Allowed&LeagueID=107644"
    data = scrape_table(url, 7)[1:]
    data[0] = [
        'Team', 
        'G', 
        'Att', 
        'Rushing Yards', 
        'Rushing TDs', 
        'Rec', 
        'Receiving Yards', 
        'Receiving TDs', 
        'FPts', 
        'FPts/G'
    ]
    for index in range(1, len(data)):
        value = data[index][0]
        start = value.index(".")+1
        end = value.index(" ")
        data[index][0] = data[index][0][start:end]
        for column_index in range(1, len(data[index])):
            value = data[index][column_index]
            if type(value) is str and  "," in value:
                data[index][column_index]=float(value.replace(",",""))
    df = pd.DataFrame(data[1:], columns=data[0])
    df = df.drop("G", axis=1)
    return df

def get_schedule(player):
    player = format_name(player)
    url = f"https://www.fantasypros.com/nfl/schedule/{player}.php"
    next_opponent = scrape_table(url, 0)[1][1]
    data = scrape_table(url, 1)[1:]
    for index in range(1, len(data)):
        data[index][0] = int(data[index][0].replace("Week ",""))
    data = [item for item in data if item[1] != 'BYE']
    df = pd.DataFrame(data[1:], columns=data[0])
    df = df.drop(columns=['Game Time', 'Matchup Rating'])
    last_week_played = float(df[df['Opp'] == next_opponent]["Week"].iloc[0])-1
    df["Played"] = df["Week"].apply(lambda x:False if x>last_week_played else True)
    return df

def get_z_score_projections(player, points_against_dfs, year=current_season):
    teams_database=get_abbreviations()
    position = get_position(player)
    points_against_df = points_against_dfs[position]
    player_df = get_player_weekly_stats(player, year)
    teams_mean = points_against_df["FPts"].mean()
    teams_st_dev = points_against_df["FPts"].std()
    projections = []
    completed_games = []
    if len(player_df)<4:
        last_year_df = get_player_weekly_stats(player, year-1)
        last_year_df["Week"]=0
        player_df = pd.concat([player_df, last_year_df], ignore_index=True)
        if len(player_df)<4:
            return None, None
    player_mean = player_df["Points"].mean()
    player_st_dev = player_df["Points"].std()
    for _, row in get_schedule(player).iterrows():
        if not row["Played"]:
            opponent = row["Opp"].replace("vs. ","").replace("@ ","")
            team = teams_database[opponent]
            team_average = points_against_df[points_against_df['Team'] == team]['FPts']
            z_score = (float(team_average.iloc[0]) - teams_mean) / teams_st_dev
            projection = player_mean + z_score*player_st_dev
            projections.append(projection)
        elif row["Week"] in player_df['Week'].values:
            fantasy_points = player_df[player_df['Week'] == row["Week"]]['Points']
            completed_games.append(float(fantasy_points.iloc[0]))
    return projections, completed_games

def process_player(player, points_against_dfs, data, lock):
    try:
        projections, _ = get_z_score_projections(player, points_against_dfs)
        if projections is not None and len(projections) > 0:
            with lock:
                data.append(
                    [
                        player,
                        round(sum(projections) / len(projections), 2)
                    ]
                )
    except:
        pass

def get_mass_z_predictions(players, year=current_season):
    points_against_dfs = {
        "WR":get_points_against("WR", year),
        "RB":get_points_against("RB", year),
        "TE":get_points_against("TE", year)
    }
    data = []
    threads = []
    data_lock = threading.Lock()
    for player in players:
        arguments = (player, points_against_dfs, data, data_lock)
        thread = threading.Thread(target=process_player, args=arguments)
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()
    return data

def get_team_stats_df(year=current_season):
    stat_type = ["passing","rushing","receiving","scoring"]
    df = None
    for stat in stat_type:
        url = f"https://www.nfl.com/stats/team-stats/offense/{stat}/{year}/reg/all"
        data = scrape_table(url)
        columns = data[0]
        if columns[1]=="Att":
            columns[1]= stat.capitalize()+" Att"
        new_df = pd.DataFrame(data[1:], columns=columns).iloc[:, :3]
        if df is None:
            df = new_df
        else:
            df = df.merge(new_df, on='Team', how='outer')
    df['Team'] = df['Team'].apply(format_team)
    df.rename(columns={'Yds': 'Rec Yds'}, inplace=True)
    return df

def team_stats(year=current_season):
    df = get_team_stats_df(year)
    output_data = {}
    for _, row in df.iterrows():
        output_data[row['Team']] = {
            "Attempts": [
                row['Passing Att'],
                row['Rushing Att']
            ],
            "TDs": [
                row["Rec TD"],
                row["Rsh TD"]
            ],
            "Yards": [
                row["Rec Yds"],
                row["Rush Yds"]
            ]
        }
    return output_data