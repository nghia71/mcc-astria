from bottle import Bottle, request, response, error, static_file, route, run
from datetime import datetime
from functools import wraps
from importlib import import_module
import json
import logging
import os
import random
from time import asctime, localtime


logger = logging.getLogger('webapp')

# set up the logger
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('logs/webapp.log')
formatter = logging.Formatter('%(msg)s')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def log_to_logger(fn):
    @wraps(fn)
    def _log_to_logger(*args, **kwargs):
        request_time = datetime.now()
        actual_response = fn(*args, **kwargs)
        if not request.url.endswith('/fetch'):
            logger.info('%s %s %s %s %s' % (
                request.remote_addr, request_time,
                request.method, request.url, response.status
            ))
        return actual_response
    return _log_to_logger

app = Bottle()
app.install(log_to_logger)

user_table = None
prob_table = None
template = None
TABLE_HEADER = '<table style="width: 100%; color: #FFF;" border="1px"><tr><th>Name</th><th>Seen</th><th>Submissions</th></tr>'
ROW_FORMATTER = '<tr><td style="text-align:center">%s</td><td style="text-align:center">%s</td><td style="text-align:center">%s</td></tr>'


def load_data(conf_file, stat_file, prob_file):
    global user_table, prob_table

    user_table = dict()
    with open(conf_file, 'rt') as uf:
        u_table = json.load(uf)
        if os.path.exists(stat_file):
            with open(stat_file, 'rt') as sf:
                user_table = json.load(sf)
            sf.close()
        else:
            user_table = dict()
        for k, v in u_table.items():
            if k not in user_table:
                user_table[k] = v
            if 'seen' not in user_table[k]:
                user_table[k]['seen'] = None
    uf.close()

    with open(prob_file, 'rt') as rf:
        prob_table = json.load(rf)
    rf.close()
    return user_table, prob_table


def dumps(info):
    with open('conf/stats.json', 'w+t') as f:
        json.dump(info, f)
    f.close()


@app.route('/', method='GET')
def index():
    return static_file('index.html', root='./')


@app.route('/img/<filename>')
def serve_static(filename):
    return static_file(filename, root='./img/')


@app.error(404)
def error404(error):
    return 'Nothing here, sorry.'


@app.route('/login/<uuid>')
def login(uuid):
    global user_table
    user_table[uuid]['seen'] = asctime()
    dumps(user_table)
    return 'OK'


@app.route('/attempt/<uuid>/<pid>')
def attempt(uuid, pid):
    global prob_table
    if not pid:
        return 'Unknow problem id %s!' % pid

    if pid in prob_table:
        input = random.choice(list(prob_table[pid].keys()))
    else:
        return 'Unknow problem id %s!' % pid

    return input


@app.route('/submit/<uuid>/<pid>/<input>/<output>')
def submit(uuid, pid, input, output):
    global user_table, prob_table

    if not pid:
        return 'Unknow problem id %s!' % pid

    if pid in prob_table:
        if input not in prob_table[pid]:
            return 'Unknow input %s for problem id %s!' % (input, pid)
        p_status = 'OK' if prob_table[pid][input] == output else 'Failed'
        user_table[uuid]['seen'] = asctime()
        if 'submit' not in user_table[uuid]:
            user_table[uuid]['submit'] = dict()
        if pid not in user_table[uuid]['submit']:
            user_table[uuid]['submit'][pid] = {'OK': 0, 'Failed': 0}
        user_table[uuid]['submit'][pid][p_status] += 1
        dumps(user_table)
    else:
        return 'Unknow problem id %s!' % pid

    return p_status


@app.route('/fetch')
def fetch_status():
    global user_table
    no_logged_users = True
    status = TABLE_HEADER
    for uuid, info in user_table.items():
        if not info['seen']:
            continue
        no_logged_users = False
        seen = info['seen']
        submits = '; '.join([
            '%s: %s' % (k, '%s' % v) for k, v in info['submit'].items()
        ])
        status += ROW_FORMATTER % (info['name'], seen, submits)
    status += '</table>'
    if no_logged_users:
        return dict(data=[])
    return dict(data=[{"status": status}])


user_table, prob_table = load_data('conf/users.json', 'conf/stats.json', 'conf/probs.json')
app.run(server='waitress', host='0.0.0.0', port='2027')
