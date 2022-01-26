from suds.client import Client
from suds import *

barcode = '11741865001806'
my_login = 'qiaPtJXdMmECFe'
my_password = '8I5ifkkh9rjz'

#coding: utf-8
import logging
logging.basicConfig(level=logging.INFO)
logging.getLogger('suds.client').setLevel(logging.DEBUG)
from suds.client import Client

url = 'https://tracking.russianpost.ru/rtm34?wsdl'
client = Client(url,retxml=True, headers={'Content-Type': 'application/soap+xml;'}, location='https://tracking.russianpost.ru/rtm34/Service.svc')

message = \
"""<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:oper="http://russianpost.org/operationhistory" xmlns:data="http://russianpost.org/operationhistory/data" xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
   <soap:Header/>
   <soap:Body>
      <oper:getOperationHistory>
         <data:OperationHistoryRequest>
            <data:Barcode>11741865001806</data:Barcode>
            <data:MessageType>0</data:MessageType>
            <data:Language>ENG</data:Language>
         </data:OperationHistoryRequest>
         <data:AuthorizationHeader soapenv:mustUnderstand="1">
            <data:login>qiaPtJXdMmECFe</data:login>
            <data:password>8I5ifkkh9rjz</data:password>
         </data:AuthorizationHeader>
      </oper:getOperationHistory>
   </soap:Body>
</soap:Envelope>"""

result = client.service.getOperationHistory(__inject={'msg':byte_str(message)})

sFile = open ("otv.txt",'w')
sFile.write(str(result))
sFile.close()