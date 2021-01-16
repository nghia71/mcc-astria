import json
import os
import sys
import uuid
import zlib

O_FILE = '../server/conf/users.tsv'
C_URL = 'http://ec2-35-174-166-72.compute-1.amazonaws.com:2027'
L_URL = 'http://127.0.0.1:2027'


def gen_conf(input_file):
    user_dict = dict()
    if os.path.exists(O_FILE):
        with open(O_FILE, 'rt') as wf:
            lines = wf.readlines()
            for line in lines:
                name, email, uid = line.strip('\n').split('\t')
                user_dict[uid] = {'name': name, 'email': email}
        wf.close()

    with open(input_file, 'rt') as rf:
        line = rf.readline()
        while line != '':
            name, email = [s.lower() for s in line.strip('\n').split('\t')]
            file_name = 'credentials/%s.conf' % name.replace(' ','_')
            if not(os.path.exists(file_name)):
                with open(file_name, 'wb') as uf:
                    uid = '%s' % uuid.uuid4()
                    uc = {
                        'name': name, 'email': email, 'uuid': uid,
                        'url': L_URL if 'local user' in name else C_URL
                    }
                    user_dict[uid] = {'name': name, 'email': email}
                    uf.write(zlib.compress(json.dumps(uc).encode()))
                uf.close()
            line = rf.readline()
    rf.close()

    with open('../server/conf/users.json', 'wt') as f:
        json.dump(user_dict, f)
    f.close()


gen_conf(sys.argv[1])
