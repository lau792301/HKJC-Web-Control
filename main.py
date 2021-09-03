# %%
from module import HKJC, MarkSix
# %%
hkjc = HKJC()
hkjc.login()

# %%
# MarkSix Control Part
hkjc.go_gaming('M6')
marksix = MarkSix(hkjc.driver)

# %%
