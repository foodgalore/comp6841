import sys
keyLogFile = input('Please input keylogger file:\n')
windowFile = input('Please input the list of window file:\n')

windowNames = ''
try:
    with open(windowFile, 'r') as windowF:
        windowNames = windowF.read()
    windowList = windowNames.split(',')
    #we have grabbed the list of window names now 
    for window in windowList:
        if window != '':
            log = ''
            try:
                with open(keyLogFile, 'r') as logF:
                    log = logF.read()
                logList = log.split('\n')
                sentence = ''
                for log in logList:
                    #this is a the logged input from the window
                    if window in log:
                        log = log.replace(window, '')
                        log = log.replace('\'', '')
                        log = log.replace('\n', '')
                        log = log.replace(' ', '')
                        log = log.replace('(space)', ' ')
                        sentence += log
                if sentence != '':
                    print(window)
                    print(sentence)

            except:
                print('{} does not exist, please try again'.format(keyLogFile))

except:
    print('{} does not exist, please try again'.format(windowFile))