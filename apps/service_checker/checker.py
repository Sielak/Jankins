import os

def getTasks2(name):
    r = os.popen('tasklist /FI "IMAGENAME eq {0}"'.format(name)).read()
    if 'No tasks are running which match the specified criteria' in r:
        print('Process is not running')
        return False
    else:
        print('Process is running')
        return True

def runTask():
    os.startfile("C:\Program Files\ConEmu\ConEmu64.exe")
    print('Process runned')


if __name__ == '__main__':
    '''
    This code checks tasklist, and run ConEmu if it will not be on tasklist
    '''

    imgName = 'ConEmu64.exe'

    r = getTasks2(imgName)
    if r is False:
        runTask()

