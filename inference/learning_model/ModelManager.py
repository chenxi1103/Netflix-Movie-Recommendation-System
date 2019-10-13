class ModelManager:
    def __init__(self, ConfigPath):
        self.config = self.loadConfig(ConfigPath)

    def loadConfig(self, filePath):
        return filePath