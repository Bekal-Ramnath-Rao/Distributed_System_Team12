class share:
    def __init__(self, name, number_of_shares):
        self.name = name
        self.number_of_shares = number_of_shares

    def __str__(self):
        return f"Name: {self.name}, Number of Shares: {self.number_of_shares}"
    
    def addshares(self, number_of_shares):
        self.number_of_shares += number_of_shares
    
    def removeshares(self, number_of_shares):
        self.number_of_shares -= number_of_shares

    def getshares(self):
        return self.number_of_shares
    
class share_handler:

    def __init__(self):
        self.share_A = share('A', 5000)
        self.share_B = share('B', 5000)

    def buy(self, number_of_share, name_of_the_share, clientshare_handler):
        print('you are making a buy')
        if name_of_the_share == 'A':
            print('No of shares available:', self.share_A.number_of_shares)
            if self.share_A.number_of_shares >= number_of_share:
                self.share_A.removeshares(number_of_share)
                clientshare_handler.update('buy', name_of_the_share, number_of_share)
                return True
            else:
                return False
        elif name_of_the_share == 'B':  
            print('No of shares available:', self.share_B.number_of_shares)
            if self.share_B.number_of_shares >= number_of_share:
                self.share_B.removeshares(number_of_share)
                clientshare_handler.update('buy', name_of_the_share, number_of_share)
                return True
            else:
                return False

    def sell(self, number_of_share, name_of_the_share, clientshare_handler):
        print('you are making a sell')
        if name_of_the_share == 'A':
            if clientshare_handler.number_of_shareA >= number_of_share:
                self.share_A.addshares(number_of_share)
                clientshare_handler.update('sell', name_of_the_share, number_of_share)
                return True
            else:
                return False
        if name_of_the_share == 'B':
            if clientshare_handler.number_of_shareB >= number_of_share:
                self.share_A.addshares(number_of_share)
                clientshare_handler.update('sell', name_of_the_share, number_of_share)
                return True
            else:
                return False

    def inquiry(self, clientshare_handler):
        print('No of Total shares available:', self.share_A.number_of_shares)
        print('No of Total shares available:', self.share_B.number_of_shares)
        print('No of share available with client:', clientshare_handler.number_of_shareA)
        print('No of share available with client:', clientshare_handler.number_of_shareB)

class clientshare_handler:
    def __init__(self,number_of_shareA, number_of_shareB ):
        self.number_of_shareA = number_of_shareA
        self.number_of_shareB = number_of_shareB

    def update(self, transaction,name_of_the_share, number_of_shares):
        if transaction == 'buy':
            if name_of_the_share == 'A':
                self.number_of_shareA += number_of_shares
            elif name_of_the_share == 'B':
                self.number_of_shareB += number_of_shares
        elif transaction == 'sell':
            if name_of_the_share == 'A':
                self.number_of_shareA -= number_of_shares
            elif name_of_the_share == 'B':
                self.number_of_shareB -= number_of_shares
        return True