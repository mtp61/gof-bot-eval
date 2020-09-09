import json


# constants
SESSION_NAME = "PPOvISMCTS"

def main():
    # get session
    with open("sessions.json", 'r') as file:
        session = json.loads(file.read())[SESSION_NAME]

    # get players
    players = []
    player_rewards = {}
    player_wins = {}
    for p in session[0].keys():
        players.append(p)
        player_rewards[p] = 0
        player_wins[p] = 0
    for g in session:
        card_sum = 0
        for p in players:
            card_sum += g[p]
            player_rewards[p] -= g[p]
        for p in players:
            if g[p] == 0:
                player_wins[p] += 1
                player_rewards[p] += card_sum

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


if __name__ == "__main__":
    main()
