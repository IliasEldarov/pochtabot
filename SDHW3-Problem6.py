class VendingMachine:

    def __init__(self):
        # means of payment - coin and bill types
        # first tuple item: value in cents. Second: if it can be returned to user as a change?
        # these items are defined on the factory
        self.coin1c = (1, True)
        self.coin5c = (5, True)
        self.coin10c = (10, True)
        self.coin25c = (25, True)
        self.billS1 = (100, False)
        self.billS5 = (500, False)
        self.billS10 = (1000, False)
        self.billS20 = (2000, False)

        self.inventory_shelves = ()
        self.inventory_shelves_capacity = ()
        self.cashier = dict()
        self.vending_items = set()
        self.inventory = dict()
        self.purchases = dict()

        self.reset()

    # use case #1 - Vendor defines which goods will be on sale and their prices
    # this is not quality of goods
    # registered vending items
    # first element of tuple: description of the item
    # second element of tuple: cost of the item in cents
    def provision(self, vending_items):
        self.vending_items = vending_items

    # use case #2 - Vendor fills the machine with items
    # index - shelf number
    # value - 2 index array - vending item type and number of loaded items
    def addInventory(self, shelf, vending_item, quantity):

        if shelf not in self.inventory_shelves:
            #unknows shelf
            return False
        #TODO reaction on exceeding shelf capacity
        # self.inventory_shelves_capacity = (20, 20, 20, 20, 10, 10, 10)

        if vending_item not in self.vending_items:
            # unknown vendingItem
            return False

        self.inventory[shelf] = [vending_item, quantity]
        return True

    # use case #2.A - Vendor gets a report on which items are left in the machine
    def infoOnInventory(self):
        return self.inventory

    # use case #3 - Vendor fills the machine with coins for change
    def loadCashier(self, cashier):
        self.cashier = cashier

    # use case #3.A - Vendor gets a report on money in the machine' cashier
    def infoOnCashier(self):
        return self.cashier

    # use case #3.B - Vendor takes money from the machine' cashier
    def substractMoneyFromCashier(self, paymentMethod, quantity):
        if cashier[paymentMethod] < quantity or quantity <= 0:
            return False
        else:
            cashier[paymentMethod] -= quantity  # 250 dollars withdrawn
            return False

    # use case #3.C - Vendor resets everything
    def reset(self):
        self.inventory_shelves = (0, 1, 2, 3, 4, 5, 7)
        self.inventory_shelves_capacity = (20, 20, 20, 20, 10, 10, 10)
        assert(len(self.inventory_shelves) == len(self.inventory_shelves_capacity))

        # cashier - current state of funds inside the machine
        # coins and bills along with their quantity
        # key - mean of payment object
        # value - current quantity of coins/bills inside the cashier
        self.cashier = dict()

        self.vending_items = set()
        # inventory - current state of machine inventory
        # key: shelf id, it has to be entered by user to purchase the item
        # value - 2-value array: [0] one of the registered vending items (see below), [1] - it's current stock, i.e. how many of them are currently available
        self.inventory = dict()

        # purchases - purchasing history
        # key: registered vending items
        # value - how many items were sold
        self.purchases = dict()

    # use case #4 - User purchases an item from shelf
    # we will assume that user
    def purcaseItem(self, shelfNumber, payments):

        insertedMoney = 0
        for payment in payments.keys():
            insertedMoney += payment[0]*payments[payment]

        good = self.inventory[shelfNumber]
        # the system checks if the requested item is available (is in stock)
        if good[1] <= 0:
            return False

        # the system detects/shows the cost of the item - $5
        print(f"The cost of the item:{good[0][1]}")

        # the system calculates amount of change:
        change = insertedMoney - good[0][1]

        # how many coins and their values to be returned is not shown here

        changeConfiguration = dict()
        # key - mean of payment object
        # value - number of coins defined by key to be returned as a change

        # let assume the missing alg. calculated that the change is 20 coins, 25 cents each
        changeConfiguration[self.coin25c] = 20

        # the state of cashier needs to be changed
        # step A - coins defined as change are marked as withdrawn to user
        if cashier[self.coin25c] >= changeConfiguration[self.coin25c]:
            cashier[self.coin25c] -= changeConfiguration[self.coin25c]

        # step B - $10 bill is marked as it is in the cashier, YES!
        cashier[self.billS10] += 1

        # the state of inventory is changed - available stock on the shelf #6 is reduced by 1
        good = self.inventory[shelfNumber]
        good[1] = good[1] - 1

        # purchases log is appened with the sold good
        if good[0] in self.purchases.items():
            self.purchases[good[0]] += 1
        else:
            self.purchases[good[0]] = 1

        print(self.purchases)
        print(self.cashier)  # transaction is logged
        print(self.inventory)  # transaction is logged

###############################################################################
# Operator-side use cases - machine management done owners of the machine
# creating machine
myMachine = VendingMachine()

# defining what it sells
mars = ("Mars bar", 200)
snickers = ("Snickers bar", 200)
snickersXXL = ("Snickers XXL bar", 200)
bounty = ("Bounty bar", 200)
coke = ("Can of Coke", 150)
dietCoke = ("Can of Diet Coke", 150)
pythonBook = ("Applying Python for Convex Problems", 500)# yes, it is expensive!
vending_items = set()
vending_items.add(mars)
vending_items.add(snickers)
vending_items.add(snickersXXL)
vending_items.add(bounty)
vending_items.add(coke)
vending_items.add(dietCoke)
vending_items.add(pythonBook)
myMachine.provision(vending_items)

# add to the machine vending items - goods
myMachine.addInventory(0, mars, 20)
myMachine.addInventory(1, mars, 20)
myMachine.addInventory(3, snickers, 10)
myMachine.addInventory(4, bounty, 10)
myMachine.addInventory(5, coke, 10)
myMachine.addInventory(6, dietCoke, 5)
myMachine.addInventory(7, pythonBook, 1)

# report on what items was loaded into machine
print(myMachine.infoOnInventory())

# loading the machine with money (we need coins for change, cards are not invented yet)
cashier = dict()
cashier[myMachine.coin1c] = 500
cashier[myMachine.coin5c] = 200
cashier[myMachine.coin10c] = 100
cashier[myMachine.coin25c] = 200
cashier[myMachine.billS1] = 0
cashier[myMachine.billS5] = 0
cashier[myMachine.billS10] = 0
cashier[myMachine.billS20] = 0
myMachine.loadCashier(cashier)

# report on money that was loaded into machine
print(myMachine.infoOnCashier())

# collect bills, these will go to a bank
myMachine.substractMoneyFromCashier(myMachine.billS5, 50) # 250 dollars withdrawn
myMachine.substractMoneyFromCashier(myMachine.billS10, 10) # 100 dollars withdrawn
###############################################################################

# User purchases an item from shelf #7 which is a Python book

payment = {myMachine.billS10: 1}
myMachine.purcaseItem(7, payment)
