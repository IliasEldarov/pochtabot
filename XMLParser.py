import xml.etree.ElementTree as ET

class ShipmentInfo():

    def __init__(self):

        self.departure_index = ''
        self.destination_index = ''
        self.sender = ''
        self.receiver = ''
        self.type = ''
        self.weight = 0.0
        self.events = []

    def get_att(self, node, path):
        if (len(path) == 2):
            return self.get_att2(node, path)
        elif (len(path) == 3):
            return self.get_att3(node, path)
        else:
            return None

    def get_att2(self, node, path):
        for child0 in node:
            if path[0] in child0.tag:
                for child1 in child0:
                    if path[1] in child1.tag:
                        return child1.text
        return None

    def get_att3(self, node, path):
        # AddressParameters->OperationAddress->Index
        for child0 in node:
            if path[0] in child0.tag:
                for child1 in child0:
                    if path[1] in child1.tag:
                        for child2 in child1:
                            if path[2] in child2.tag:
                                return child2.text
        return None

shipment = ShipmentInfo()

envelope = ET.parse('otv.xml').getroot()
body = envelope[0]
getOperationHistoryResponse = body[0]
operationHistoryData = getOperationHistoryResponse[0]

firstEvent = True
for historyRecord in operationHistoryData:
    shipment.events.append( (
        shipment.get_att(historyRecord, ["OperationParameters", "OperType", "Name"]),
        shipment.get_att(historyRecord, ["OperationParameters", "OperDate"])
    )
    )

    if not firstEvent:
        continue

    shipment.departure_index = shipment.get_att(historyRecord, ["AddressParameters", "OperationAddress", "Index"])
    shipment.destination_index = shipment.get_att(historyRecord, ["AddressParameters", "DestinationAddress", "Index"])
    shipment.sender = shipment.get_att(historyRecord, ["UserParameters", "Sndr"])
    shipment.receiver = shipment.get_att(historyRecord, ["UserParameters", "Rcpn"])
    shipment.type = shipment.get_att(historyRecord, ["ItemParameters", "ComplexItemName"])
    shipment.weight = shipment.get_att(historyRecord, ["ItemParameters", "Mass"])

    firstEvent = False
print(shipment.events)
print(shipment.departure_index, shipment.destination_index, shipment.sender, shipment.receiver, shipment.type, shipment.weight)
'''
AddressParameters->DestinationAddress->Index 'Kuda'
AddressParameters->OperationAddress->Index 'otkuda'
ItemParameters->ComplexItemName  'pismo'
ItemParameters->MailCtg->Mass

UserParameters->Sndr #'oppravitel
UserParameters->Rcpn # poluchatel

OperationParameters->OperType->Name  'acceptance'
OperationParameters->OperAttr->OperDate "date"

'''