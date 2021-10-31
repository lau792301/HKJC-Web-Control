# %%
from modules import HKJC, Marksix
# %%
hkjc = HKJC()
# hkjc.login()
# hkjc.get_account_balance()

# %%
# MarkSix Control Part
hkjc.go_gaming('M6')
ms = Marksix(hkjc.driver)
ms_next_game_info = ms.get_next_game_info()
ms_next_game_date = ms_next_game_info['Draw Date']
# marksix.buy_single([21, 15, 35, 9, 4, 49])
# marksix.buy_multi([1,2,3,4,5,6,7], is_full_ratio=False)
# marksix.buy_banker(main_list= [1,2,3], sub_list=[4,5,6,15,16,17,18], is_full_ratio=False)
# marksix.buy_random(gaming_type= 'single')
# marksix.buy_random(gaming_type='multi', num_ball = 8)
# marksix.buy_random(gaming_type = 'banker', num_bet = 3, main_num_ball = 3, sub_num_ball = 4)
# hkjc.send_bet()
# %%
