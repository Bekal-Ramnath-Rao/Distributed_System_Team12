class share_handler:

    def __init__(self):
        self.shares = {"A" : 5000, "B" : 5000}

    def buy(self, number_of_share, name_of_the_share):
        if 'A' in name_of_the_share:
            if self.shares['A'] >= number_of_share:
                self.shares['A'] -= number_of_share
                return True
            else:
                return False
        elif 'B' in name_of_the_share:
            if self.shares['B'] >= number_of_share:
                self.shares['B'] -= number_of_share
                return True
            else:
                return False


    def sell(self, number_of_share, name_of_the_share):
        if 'A' in name_of_the_share:
            self.shares['A'] += number_of_share
            return True
        elif 'B' in name_of_the_share:
            self.shares['B'] += number_of_share
            return True

    def inquiry():
        'Here we have to print the history of transaction - implementation not done yet'

