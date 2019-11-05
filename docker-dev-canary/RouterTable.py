import random

"""
The RouterTable class.

In the jargon, control is our baseline model. It can be the original model in this comparison.
Treatment is the new model that we want to test against the old model.
"""
class RouterTable:
    def __init__(self, port):
        # The port of our control model
        self.control_port = port
        # The port of our treat model
        self.treat_port = -1
        # The mapping from user_id to self.CONTROL or self.TREAT
        self.user_to_group = {}
        # How many traffic are we directing into treat model
        self.treat_percentage = 0

        self.CONTROL = "CONTROL"
        self.TREAT = "TREAT"

    def flush(self):
        self.user_to_group = {}
        self.treat_percentage = 0

    def get_port_by_user_id(self, user_id):
        if not self.is_in_test():
            return self.control_port

        # If we have not seen this user before, we first assign it to a group according to self.treat_percentage.
        if user_id not in self.user_to_group:
            self.assign_new_user(user_id)

        if self.user_to_group[user_id] == self.CONTROL:
            return self.control_port
        else:
            return self.treat_port

    def is_user_in_treatment(self, user_id):
        group = self.get_group_by_user_id(user_id)
        if group == self.TREAT:
            return True
        return False

    def get_group_by_user_id(self, user_id):
        if user_id not in self.user_to_group:
            self.assign_new_user(user_id)
        return self.user_to_group[user_id]

    """
    This is used in canary tests to incrementally increase the traffic.
    However, do remember to be aware of the logging of data because for a particular user_id, 
    you may be using a different model than the last time.
    """
    def set_treat_percentage(self, percentage):
        self.user_to_group = {}
        self.treat_percentage = percentage

    """
    For the user we have not seen before, we add him/her into our map.
    """
    def assign_new_user(self, user_id):
        r = random.random()
        if r <= self.treat_percentage:
            # It should be in treatment group.
            self.user_to_group[user_id] = self.TREAT
        else:
            self.user_to_group[user_id] = self.CONTROL

    """
    This is used to setup a new treatment.
    """
    def set_new_treatment(self, port, percentage):
        self.treat_port = port
        self.treat_percentage = percentage
        self.user_to_group = {}

    """
    This is used when the test is successful. Then the treatment becomes the new control.
    """
    def test_success(self):
        self.control_port = self.treat_port
        self.user_to_group = {}
        self.treat_percentage = 0

    """
    This is used when the test is failed. Then the control keeps being the control.
    """
    def test_fail(self):
        self.user_to_group = {}
        self.treat_percentage = 0

    def is_in_test(self):
        return self.treat_percentage != 0

