"""
    A/B Testing Canary Testing Part in the supervisor module draft
"""

UserIdContainerMap = None
DeploymentStatus = 'InfrastructureAvailable'

"""
    Read config file ABTestConfig.json or NewModelDeploy.json and get config dict
"""
def readConfig(configfile):
    # config = parse(configfile)
    # return config
    raise NotImplemented

"""
    Excute a new deployment according to config. 
"""
def excutor(configfile, logpath):
    # config = readConfig()

    # if is New Model Deployment
    #   update(UserIdContainerMap, config)
    #   sleep(config)
    #   analyzeLog(logPath)
    #   update(UserIdContainerMap, config)
    #   sleep(config)
    #   analyzeLog(logPath)
    #   ...
    #   if not performing well:
    #       rollback_to_previous_version()
    #   report()

    # if is A/B test experiment
    #   ....
    raise NotImplemented

"""
    Return containerId given userId according to UserIdContainerMap (Need not to be a dict)
"""
def router(userId):
    # return UserIdContainerMap[userId]
    raise NotImplemented

"""
    Update UserIdContainerMap according to config
"""
def update():
    raise NotImplemented

"""
    Analyze model performance according to the log
"""
def analyzeLog(logPath):
    raise NotImplemented


"""
    Decide whether to excute the new deployment
"""
def whenSuperviserReceiveNewConfiguration():
    global DeploymentStatus
    if DeploymentStatus == 'InfrastructureAvailable':
        DeploymentStatus = 'InfrastructureNotAvailable'
        excutor(None, None)
    elif DeploymentStatus == 'InfrastructureNotAvailable':
        #reportFailure()
        pass

"""
    *************************************************
"""

"""
    Infrastructure Part in the supervisor module draft
"""
def receiveRequestAndSendToAccordingContainer(apistring):
    # userid = parse(apistring)
    # containerid = router(userId)
    # response = sendRequestandReceiveResponse(containerid)
    # logResponse(response,logPath)
    # sendBackToUser(response)
    raise NotImplemented

def receiveConfigurationRequest(apistring):
    # whenSuperviserReceiveNewConfiguration()
    raise NotImplemented