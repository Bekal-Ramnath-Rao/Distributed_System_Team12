import json

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
    
    def to_dict(self):
        """Convert the object to a dictionary for JSON serialization."""
        return {
            "name": self.name,
            "number_of_shares": self.number_of_shares
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create an object from a dictionary."""
        instance = cls(data["name"], data["number_of_shares"])
        return instance

# Custom JSON Encoder
class shareEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, share):
            return obj.to_dict()  # Serialize using the to_dict method
        return super().default(obj)
    
class share_handler:

    def __init__(self, share_A=None, share_B=None):
        if share_A is not None or share_B is not None:
            self.share_A = share.from_dict(share_A)
            self.share_B = share.from_dict(share_B)
        else:
            self.share_A = share('A', 5000)
            self.share_B = share('B', 5000)

    def buy(self, number_of_share, name_of_the_share, clientshare_handler, client_name):
        print('you are making a buy')
        if name_of_the_share == 'A':
            print('No of shares available:', self.share_A.number_of_shares)
            if self.share_A.number_of_shares >= number_of_share:
                self.share_A.removeshares(number_of_share)
                clientshare_handler.update('buy', name_of_the_share, number_of_share, client_name)
                return True
            else:
                return False
        elif name_of_the_share == 'B':  
            print('No of shares available:', self.share_B.number_of_shares)
            if self.share_B.number_of_shares >= number_of_share:
                self.share_B.removeshares(number_of_share)
                clientshare_handler.update('buy', name_of_the_share, number_of_share, client_name)
                return True
            else:
                return False

    def sell(self, number_of_share, name_of_the_share, clientshare_handler, client_name):
        print('you are making a sell')
        if name_of_the_share == 'A':
            if client_name not in clientshare_handler.client_data:
                    clientshare_handler.client_data[client_name] = {'A': 0, 'B': 0}
            if clientshare_handler.client_data[client_name][name_of_the_share] >= number_of_share:
                self.share_A.addshares(number_of_share)
                clientshare_handler.update('sell', name_of_the_share, number_of_share,client_name)
                return True
            else:
                return False
        if name_of_the_share == 'B':
            if client_name not in clientshare_handler.client_data:
                    clientshare_handler.client_data[client_name] = {'A': 0, 'B': 0}
            if clientshare_handler.client_data[client_name][name_of_the_share] >= number_of_share:
                self.share_A.addshares(number_of_share)
                clientshare_handler.update('sell', name_of_the_share, number_of_share, client_name)
                return True
            else:
                return False

    def inquiry(self, clientshare_handler, client_name):
        if client_name not in clientshare_handler.client_data:
            clientshare_handler.client_data[client_name] = {'A': 0, 'B': 0}
        return clientshare_handler.client_data[client_name]
    
    def to_dict(self):
        """Convert the object to a dictionary for JSON serialization."""
        return {
            "share_A": self.share_A,
            "share_B": self.share_B
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create an object from a dictionary."""
        instance = cls(data["share_A"], data["share_B"])
        return instance

# Custom JSON Encoder
class shareHandlerEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, share_handler) or isinstance(obj, share):
            return obj.to_dict()  # Serialize using the to_dict method
        return super().default(obj)

class clientshare_handler:
    def __init__(self,number_of_shareA, number_of_shareB, name_of_the_client):
        self.number_of_shareA = number_of_shareA
        self.number_of_shareB = number_of_shareB
        self.client_data = {}
        self.client_data[name_of_the_client] = {'A': 0, 'B': 0}

    def update(self, transaction,name_of_the_share, number_of_shares, client_name):
        if transaction == 'buy':
            if name_of_the_share == 'A':
                self.number_of_shareA += number_of_shares
                if client_name not in self.client_data:
                    self.client_data[client_name] = {'A': 0, 'B': 0}
                self.client_data[client_name][name_of_the_share] += number_of_shares
            elif name_of_the_share == 'B':
                self.number_of_shareB += number_of_shares
                if client_name not in self.client_data:
                    self.client_data[client_name] = {'A': 0, 'B': 0}
                self.client_data[client_name][name_of_the_share] += number_of_shares
        elif transaction == 'sell':
            if name_of_the_share == 'A':
                self.number_of_shareA -= number_of_shares 
                self.client_data[client_name][name_of_the_share] -= number_of_shares
            elif name_of_the_share == 'B':
                self.number_of_shareB -= number_of_shares
                self.client_data[client_name][name_of_the_share] -= number_of_shares
        return True

    def to_dict(self):
        """Convert the object to a dictionary for JSON serialization."""
        return {
            "number_of_shareA": self.number_of_shareA,
            "number_of_shareB": self.number_of_shareB,
            "client_data": self.client_data
        }

    @classmethod
    def from_dict(cls, data):
        """Create an object from a dictionary."""
        instance = cls(data["number_of_shareA"], data["number_of_shareB"], list(data["client_data"].keys())[0])
        instance.client_data = data["client_data"]
        return instance


# Custom JSON Encoder
class ClientShareHandlerEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, clientshare_handler):
            return obj.to_dict()  # Serialize using the to_dict method
        return super().default(obj)
