from src.handler import Handler


main_menu = Handler(
    name='Main menu',
    component='MainMenu',
    method='welcome'
)
main_menu.add_children(game_menu_item := Handler(
    name='Start new game',
    component='Game',
    method='start_game'
))
main_menu.add_children(Handler(
    name='Ranking table',
    component='MainMenu',
    method='ranking_table'
))
main_menu.add_children(Handler(
    name='Past games statistics',
    component='MainMenu',
    method='player_statistic'
))
main_menu.add_children(management_menu_item := Handler(
    name='Management',
    component='MainMenu',
    method='management'
))
main_menu.add_children(Handler(
    name='Exit game',
    component='MainMenu',
    method='exit_game'
))
management_menu_item.add_children(player_list_menu_item := Handler(
    name='Player table',
    component='Management',
    method='player_list'
))
management_menu_item.add_children(Handler(
    name='Create player',
    component='Management',
    method='player_create'
))
management_menu_item.add_children(Handler(
    name='Delete player',
    component='Management',
    method='player_delete'
))
management_menu_item.add_children(Handler(
    name='Create new league season',
    component='Management',
    method='new_league_season'
))
management_menu_item.add_children(Handler(
    name='Previous',
    component='Utility',
    method='previous_menu_item'
))
