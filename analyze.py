import json
from scipy.stats import ttest_ind


# constants
SESSION_NAME = "PPOvISMCTS"

def main():
    # get session
    with open("sessions.json", 'r') as file:
        session = json.loads(file.read())[SESSION_NAME]

    # get players
    players = []
    player_rewards = {}
    player_rewards_list = {}
    player_wins = {}
    for p in session[0].keys():
        players.append(p)
        player_rewards[p] = 0
        player_wins[p] = 0
        player_rewards_list[p] = []
    for g in session:
        card_sum = 0
        for p in players:
            card_sum += g[p]
            player_rewards[p] -= g[p]
        for p in players:
            if g[p] == 0:
                win_player = p
                player_wins[p] += 1
                player_rewards[p] += card_sum
                break
        for p in players:
            if p == win_player:
                player_rewards_list[p].append(card_sum)
            else:
                player_rewards_list[p].append(-g[p])
                

    num_games = len(session)
    player_info = []
    for p in players:
        player_info.append((p, player_rewards[p] / num_games, player_wins[p] / num_games))
    
    player_info.sort(key=lambda i: -i[1])

    # print info
    print(f"{ num_games } games in session")
    print("name,\t\t avg reward,\t win percentage")
    for i in player_info:
        print(f"{ i[0] },\t { round(i[1], 2) },\t\t { round(i[2], 2) }")

    # staticitical significance
    # group the players and get the stats
    player_groups = []
    group_stats = {}
    for p in players:
        p_short = p[:-1]
        if p_short not in player_groups:
            player_groups.append(p_short)
            group_stats[p_short] = []
        group_stats[p_short].extend(player_rewards_list[p])

    # print staticical significance info
    if len(player_groups) == 2:  # only works with two players
        print()
        print(f"difference of means p = { round(ttest_ind(group_stats[player_groups[0]], group_stats[player_groups[1]]).pvalue, 4) }")

if __name__ == "__main__":
    main()


