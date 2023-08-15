from scraper import get_player_weekly_stats
import pandas as pd

class DataManager:

    def __init__(self):
        self.df = {}
    
    def get_df(self):
        return self.df

    def add_new_player_data(self, new_player):
        try:
            new_data = get_player_weekly_stats(new_player)
        except:
            new_data = pd.DataFrame(columns=['Week'])
        self.df[new_player] = new_data

    def format_player_list(self, player, stat):
        updated_list = []
        player_df = self.df[player]
        for week in range(1, 19):
            if (player_df['Week'] == week).any():
                updated_list.append(float(player_df[player_df["Week"] == week][stat].iloc[0]))
            else:
                updated_list.append(float('nan'))
        return updated_list

    def get_data(self, players, stat):
        output = []
        for player in players:
            if player not in self.df.keys():
                self.add_new_player_data(player)
            output.append(
                [
                    player,
                    self.format_player_list(player, stat)
                ]
            )
        return output

    def clear(self):
        self.df = {}