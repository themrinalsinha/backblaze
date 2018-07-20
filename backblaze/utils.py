from subprocess  import check_output, CalledProcessError
from collections import namedtuple

def _get_output(command):
    result = namedtuple('result', ['status', 'data'])
    try:
        result.data   = [x for x in check_output(command.split(' '), \
                        shell=True).decode('utf-8').split('\n') if x]
        result.status = True
        return result
    except CalledProcessError as error:
        result.status = False
        result.data   = error.output
        return result
