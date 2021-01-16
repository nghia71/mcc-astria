import json
import os
import sys
import uuid
import zlib

PROBLEM_DICT = {
    'next_prime': {"1": "2", "3": "3", "1000000000": "1000000007"},
    'fake_coin': {"11011111": "2", "11111110": "7", "11101111": "3"},
    'move_sequence': {"4": "43816729", "8": "81672943", "9": "92761834"}
}


def gen_conf():
    with open('../server/conf/probs.json', 'wt') as f:
        json.dump(PROBLEM_DICT, f)
    f.close()


gen_conf()
