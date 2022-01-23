class VendingMachine:

    def __init__(self):
        # means of payment - coin and bill types
        # first tuple item: value in cents. Second: if it can be returned to user as a change?
        # defined on factory and can not be altered by operator

        self.coin1c = (1, True)
        self.coin5c = (5, True)
        self.coin10c = (10, True)
        self.coin25c = (25, True)
        self.billS1 = (100, True)
        self.billS5 = (500, False)
        self.billS10 = (1000, False)
        self.billS20 = (2000, False)

        # shelfs and their capacities are defined on factory and can not be altered by operator
        self.inventory_shelves = (0, 1, 2, 3, 4, 5, 6, 7)
        self.inventory_shelves_capacity = (20, 20, 20, 20, 10, 10, 10, 10)
        assert(len(self.inventory_shelves) == len(self.inventory_shelves_capacity))

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
            print("cant add item to unknown shelf")
            return False

        if shelf not in self.inventory.keys():
            if quantity > self.inventory_shelves_capacity[shelf]:
                print("cant add item to shelf - exceeding capacity")
                return False
        elif self.inventory[shelf][1] + quantity > self.inventory_shelves_capacity[shelf]:
            print("cant add item to shelf - exceeding capacity")
            return False

        if vending_item not in self.vending_items:
            # unknown vendingItem
            print("cant add item to shelf - unknows item")
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
            return True

    # use case #3.C - Vendor resets everything
    def reset(self):

        # cashier - current state of funds inside the machine
        # coins and bills along with their quantity
        # key - mean of payment object
        # value - current quantity of coins/bills inside the cashier
        self.cashier = dict()

        self.vending_items = set()
        # inventory - current state of machine inventory
        # key: shelf id, it has to be entered by user to purchase the item
        # value - 2-value array: [0] one of the registered vending items (see below),
        # [1] - it's current stock, i.e. how many of them are currently available
        self.inventory = dict()

        # purchases - purchasing history
        # key: registered vending items
        # value - how many items were sold
        self.purchases = dict()

    # use case #4 - User purchases an item from shelf
    # we will assume that user
    def purcaseItem(self, shelfNumber, payments):
        #print("Purchasing of an item by user")
        insertedMoney = 0
        for payment in payments.keys():
            insertedMoney += payment[0]*payments[payment]

        if shelfNumber not in self.inventory_shelves:
            print("Unknown shelf")
            return False

        good = self.inventory[shelfNumber]
        # the system checks if the requested item is available (is in stock)
        if good[1] <= 0:
            print("Out of stock for the item")
            return False

        if insertedMoney < good[0][1]:
            print("Payment is not enough to purchase the item")
            return False

        # the system detects/shows the cost of the item - $5
        print(f"Inserted {insertedMoney} cents, the cost of the item is {good[0][1]} cents")

        # the system calculates amount of change due:
        changeAmount = insertedMoney - good[0][1]

        # we need to calculate how many coins and their values to be returned
        changeConfiguration = self._getChangeConfiguration(changeAmount)
        if changeConfiguration is None:
            # in some cases we will have to refuse purchase because we ran out of change
            print("Ran out of change or exact change not possible")
            return False

        # the state of cashier needs to be changed
        # step A - coins for change are marked as withdrawn to user
        if changeConfiguration:
            print("User, take you change:")

        for paymentMethod in changeConfiguration.keys():
            print(f"{paymentMethod[0]} cents x {changeConfiguration[paymentMethod]}")
            cashier[paymentMethod] -= changeConfiguration[paymentMethod]

        if changeConfiguration:
            print(f"Total change: {changeAmount} cents")

        #if cashier[self.coin25c] >= changeConfiguration[self.coin25c]:
        #    cashier[self.coin25c] -= changeConfiguration[self.coin25c]

        # step B - inserted payment needs to marked as it is in the cashier
        #cashier[self.billS10] += 1
        for payment in payments.keys():
            cashier[payment] += payments[payment]

        # the state of inventory is changed - available stock on the shelf #6 is reduced by 1
        good = self.inventory[shelfNumber]
        good[1] = good[1] - 1

        # purchases log is appended with the sold good
        if good[0] in self.purchases.items():
            self.purchases[good[0]] += 1
        else:
            self.purchases[good[0]] = 1

        #print(self.purchases)
        #print(self.cashier)  # transaction is logged
        #print(self.inventory)  # transaction is logged
        return True

    # alg calculates change, minimizing number of coins to be returned
    # this protected function
    def _getChangeConfiguration(self, changeAmount):
        # Alg should return changeConfiguration where
        # key - mean of payment object
        # value - number of coins defined by key to be returned as a change

        changeConfiguration = dict()
        scannedPaymentMethods = set()
        while changeAmount != 0:

            paymentOption, availableAuantity = self._calculateChange(changeAmount, scannedPaymentMethods)

            if not paymentOption:
                # we ran out of options to find exact change
                return None

            scannedPaymentMethods.add(paymentOption)
            thisRequiredNumber = int(changeAmount / paymentOption[0])
            usedCoins = min(availableAuantity, thisRequiredNumber)
            if not usedCoins:
                continue

            changeAmount -= usedCoins*paymentOption[0]
            changeConfiguration[paymentOption] = usedCoins

        return changeConfiguration

    def _calculateChange(self, amount, scannedPaymentMethods):
        maxAmount = 0
        maxAmountPaymentMethod = None
        for paymentMethod in cashier.keys():
            if paymentMethod not in scannedPaymentMethods and paymentMethod[0] > maxAmount and paymentMethod[1]:
                maxAmount = paymentMethod[0]
                maxAmountPaymentMethod = paymentMethod

        return maxAmountPaymentMethod, cashier[maxAmountPaymentMethod] if maxAmountPaymentMethod else None
#
# Operator-side use cases - machine management
#
# instantiating machine
myMachine = VendingMachine()

# operator defined what vending items the machine will be capable to sell
mars = ("Mars bar", 200)
snickers = ("Snickers bar", 200)
snickersXXL = ("Snickers XXL bar", 200)
bounty = ("Bounty bar", 200)
coke = ("Can of Coke", 150)
dietCoke = ("Can of Diet Coke", 150)
pythonBook = ("Applying Python for Convex Problems", 506)# yes, it is expensive!
vending_items = set()
vending_items.add(mars)
vending_items.add(snickers)
vending_items.add(snickersXXL)
vending_items.add(bounty)
vending_items.add(coke)
vending_items.add(dietCoke)
vending_items.add(pythonBook)
myMachine.provision(vending_items)

# operator loads vending items to the machine
myMachine.addInventory(0, mars, 30) # fail - exceed capacity of shelf
myMachine.addInventory(1, mars, 20)
myMachine.addInventory(2, mars, 15)
myMachine.addInventory(2, mars, 15)
myMachine.addInventory(3, snickers, 10)
myMachine.addInventory(4, bounty, 10)
myMachine.addInventory(5, coke, 10)
myMachine.addInventory(6, dietCoke, 5)
myMachine.addInventory(7, pythonBook, 1)
myMachine.addInventory(8, dietCoke, 5)# fail - no such shelf
# operator gets report on what items were loaded into machine
print(myMachine.infoOnInventory())

# operator loads the machine with coins
# machine need coins for change, because credit cards are not invented yet
cashier = dict()
cashier[myMachine.coin1c] = 500
cashier[myMachine.coin5c] = 200
cashier[myMachine.coin10c] = 100
cashier[myMachine.coin25c] = 200
cashier[myMachine.billS1] = 5
cashier[myMachine.billS5] = 0
cashier[myMachine.billS10] = 0
cashier[myMachine.billS20] = 0
myMachine.loadCashier(cashier)

# operator prints report about money that were loaded into machine
print(myMachine.infoOnCashier())

# operator collects bills (after some time the machine was used)
myMachine.substractMoneyFromCashier(myMachine.billS5, 50) # 250 dollars withdrawn
myMachine.substractMoneyFromCashier(myMachine.billS10, 10) # 100 dollars withdrawn
###############################################################################
###############################################################################
###############################################################################
###############################################################################
#
# User side use cases including a few negative cases
#
# User wants to purchase an item from shelf
# TC 1
myMachine.purcaseItem(77, {myMachine.coin25c: 1}) # fail - vending item is not found

# TC 2
myMachine.purcaseItem(7, {myMachine.billS20: 50}) # fail - can not find exact change to return

# TC 3
myMachine.purcaseItem(7, {myMachine.coin25c: 1})  # fail - payment is not enough

# TC 4 - user wants to purchase a Python book
# notice that 5 of 100 cent bills were given as a change and 10 bill got into cashier
#print(myMachine.infoOnCashier())
myMachine.purcaseItem(7, {myMachine.billS10: 1})  # SUCCESS!
#print(myMachine.infoOnCashier())


# TC 5
myMachine.purcaseItem(7, {myMachine.billS10: 1})  # fail - out of stock

