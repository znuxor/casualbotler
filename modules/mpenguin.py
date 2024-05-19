# coding=utf8
"""
A kit of mpenguin-related code
"""
import datetime
import os
import sys
import sopel.module

# hack for relative import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import from_admin_channel_only

PRIV_BIT_MASK = (sopel.module.HALFOP | sopel.module.OP | sopel.module.ADMIN | sopel.module.OWNER)


def configure(config):
    '''Invoked upon parameter configuration mode'''
    pass


def setup(bot):
    '''Invoked when the module is loaded.'''
    pass

duckKickOn = False


@sopel.module.interval(60)
def set_duck_kick(bot):
    '''Enables duck kick during legal weekend hours.'''
    global duckKickOn

    todayDate = datetime.datetime.utcnow()
    todayDayOfWeek = todayDate.weekday()
    todayHour = todayDate.hour
    if todayDayOfWeek == 0:  # Monday
        if todayHour >= 12:  # Baker Island is UTC-12:00
            if duckKickOn:
                duckKickOn = False
                bot.say(".duckkick disable", '#casualconversation')
    elif todayDayOfWeek == 4:  # Friday
        if todayHour >= (24-14):  # Kiribati Lines Islands are UTC+14:00
            if not duckKickOn:
                duckKickOn = True
                bot.say(".duckkick enable", '#casualconversation')
