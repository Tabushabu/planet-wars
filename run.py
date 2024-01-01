import subprocess
import os, sys


def show_match(bot1_xml, bot1_tree_name, bot2_xml, bot2_tree_name, map_num):
    """
        Runs an instance of Planet Wars between the two given bots on the specified map. After completion, the
        game is replayed via a visual interface.
    """

    command = 'java -jar tools/PlayGame.jar maps/map' + str(map_num) + '.txt 1000 1000 log.txt ' + \
              '"python bt_bot.py ' + bot1_xml + ' ' + bot1_tree_name + '" ' + \
              '"python bt_bot.py ' + bot2_xml + ' ' + bot2_tree_name + '" ' + \
              '| java -jar tools/ShowGame.jar'
    print(command)
    os.system(command)


def test(bot1, bot2, map_num):
    """ Runs an instance of Planet Wars between the two given bots on the specified map. """
    bot_name, opponent_name = bot1.split('/')[1].split('.')[0], bot2.split('/')[1].split('.')[0]
    print('Running test:',bot_name,'vs',opponent_name)
    command = 'java -jar tools/PlayGame.jar maps/map' + str(map_num) +'.txt 1000 1000 log.txt ' + \
              '"python ' + bot1 + '" ' + \
              '"python ' + bot2 + '" '

    print(command)
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)

    while True:
        return_code = p.poll()  # returns None while subprocess is running
        line = p.stdout.readline().decode('utf-8')
        if '1 timed out' in line:
            print(bot_name,'timed out.')
            break
        elif '2 timed out' in line:
            print(opponent_name,'timed out.')
            break
        elif '1 crashed' in line:
            print(bot_name, 'crashed.')
            break
        elif '2 crashed' in line:
            print(opponent_name, 'crashed')
            break
        elif 'Player 1 Wins!' in line:
            print(bot_name,'wins!')
            break
        elif 'Player 2 Wins!' in line:
            print(opponent_name,'wins!')
            break

        if return_code is not None:
            break

def run_game(bot1_xml, bot1_tree_name, bot2_xml, bot2_tree_name, map_num):
    show_match(bot1_xml, bot1_tree_name, bot2_xml, bot2_tree_name, map_num)

if __name__ == '__main__':
    bot1_xml, bot1_tree_name, bot2_xml, bot2_tree_name, map_num = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]
    #maps = [71, 13, 24, 56, 7]

    show = len(sys.argv) < 2 or sys.argv[1] == "show"
        # use this command if you want to observe the bots
    
    run_game(bot1_xml, bot1_tree_name, bot2_xml, bot2_tree_name, map_num)
    
    #if show:
    #    show_match(bot1_xml, bot1_tree_name, bot2_xml, bot2_tree_name, map_num)
    #else:
    #    # use this command if you just want the results of the matches reported
    #    test(bot1, bot2, map_num)
