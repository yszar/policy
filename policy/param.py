# -*- coding: utf-8 -*-
CODE = ['000009', '000008', '000007']
XLSX = 'stcokcode_test.xlsx'
SAVE_PATH = "pdfs"

# 1.12 策略
# CV = ['累计投票', '累积投票']
# SB = [['改选', '更换', '更替', '替换', '变更'], ['不得超过', '不超过'], ['董事', ]]
# TL = [['连续', ], ['以上', ], ['提名', '候选'], ['董事', ]]
# SL = [['董事', ], ['提名', '候选'], ['股份', ], ['以上', ]]
# QE = '进行审查'
# AM = [['特别决议', '股东大会'], ['表决权', ], ['以上'], ['通过', ]]
# GP = [['董事', '高级管理'], ['补偿', '赔偿'], ['赔偿', '责任']]

# 1.06策略
# CV = ['累计投票', '累积投票']
# SB = [['改选', '更换', '更替', '替换', '变更'], ['不得超过', '不超过'], ['董事', ], ['提名', ]]
# TL = [['持股'], ['连续', ], ['以上', ], ['提名', '候选'], ['董事', ]]
# SL = [['董事', ], ['提名', '候选'], ['股份', ], ['以上', ], ['百分之三', '3%', '百分之五', '5%']]
# QE = '进行审查'
# AM = [['特别决议', '股东大会'], ['表决权', ], ['以上'], ['通过', ]]
# GP = [['董事', '高级管理'], ['补偿', '赔偿'], ['赔偿', '责任']]

# 1.13 策略
CV = ['累计投票', '累积投票']
SB = [['改选', '更换', '更替', '替换', '变更'], ['不得超过', '不超过'], ['分之', '/'], ['董事', ],
      ('利润', '兼任', '资产', '股份')]
TL = [['连续', ], ['天', '日', '月'], ['以上', ], ['提名', '候选'], ['董事', ],
      ('出席', '利润', '诉讼')]
SL = [['董事', ], ['提名', '候选'], ['股份', ], ['%', '百分之'], ['以上', ], ('职责',)]
QE = '进行审查'
AM = [['特别决议', '股东大会'], ['表决权', ], ['以上'], ['通过', ]]
GP = [['董事', '高级管理'], ['补偿', '赔偿'], ('赔偿责任',)]
