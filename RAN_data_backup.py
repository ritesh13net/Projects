import time
import random
import csv

class RANData:
    def __init__(self) -> None:
        self.data = []
        # self.data4g = []
        self.ns = {
            'un' : 'utranNrm.xsd',
            'xn' : 'genericNrm.xsd',
            'gn' : 'geranNrm.xsd',
            'cd' : 'configData.xsd',
            'es' : 'EricssonSpecificAttributes.xsd',
            }
        self.nci_5g = {}
        self.cell_region = {}
        self.get_cell_region('cell_region.csv')


    def meContext_manageElement_check(self, meContext):
        response_4g = {}
        response_5g = {}
        try:
            gNBId_element = self.getvalFromElem(meContext, 'es', 'gNBId')
            eNBId = self.getvalFromElem(meContext, 'es', 'eNBId')
            if eNBId is not None:# meContext.getparent().get("id")[0:5] == '188031':# and meContext.get("id") == 'NEEG01':
                response_4g['rat'] = '4G'
                # response_4g['id'] = meContext.getparent().get("id")
                response_4g['lte_enodeb_name'] = meContext.get("id")
                DataContainer = meContext.find("{genericNrm.xsd}ManagedElement").findall("{genericNrm.xsd}VsDataContainer")
                result = list(map(lambda p: self._4GENodeBFunction(p, response_4g), DataContainer))
                # [self.ENodeBFunction(p, response) for p in DataContainer]
                DataContainer.clear()
            if gNBId_element is not None: # meContext.getparent().get("id")[0:3] == 'JUM':# and meContext.get("id") == 'FRUI05':
                response_5g['rat'] = '5G'
                response_5g['nr_cell_id'] = meContext.getparent().get("id")
                response_5g['nr_gnodeb_name'] = meContext.get("id")
                DataContainer = meContext.find("{genericNrm.xsd}ManagedElement").findall("{genericNrm.xsd}VsDataContainer")
                # DataContainer = self.getAllFromElem(elem=meContext, namespace='gn', key='VsDataContainer')
                result = list(map(lambda p: self._5GGNBFunction(p, response_5g), DataContainer))
                DataContainer.clear()
        except Exception as e:
            print(f"An error occurred: {e}")

    def _5GGNBFunction(self, vsDataContainer, response_5g):
        try:
            GNBCUCPFunction = self.getElemFromElem(elem=vsDataContainer, namespace='es', key='vsDataGNBCUCPFunction')
            if GNBCUCPFunction is not None:
                response_5g['mcc'] = self.getvalFromElem(GNBCUCPFunction, 'es', 'mcc')
                response_5g['mnc'] = self.getvalFromElem(GNBCUCPFunction, 'es', 'mnc')

            GNBCUUPFunction = self.getElemFromElem(elem=vsDataContainer, namespace='es', key='vsDataS1ULink')
            if GNBCUUPFunction is not None:
                response_5g['nr_gnodeb_ip'] = self.getvalFromElem(GNBCUUPFunction, 'es', 'localEndPoint')

            GNBDUFunction = self.getElemFromElem(elem=vsDataContainer, namespace='es', key='vsDataGNBDUFunction')
            if GNBDUFunction is not None:
                response_5g['nr_gnodeb_id'] = self.getvalFromElem(elem=GNBDUFunction, namespace='es', key='gNBId')
                gnbname = self.getvalFromElem(elem=GNBDUFunction, namespace='es', key='gNBDUName')
                if gnbname != None:
                    response_5g['nr_gnodeb_name'] = gnbname

            DataContainers = vsDataContainer.findall("./{genericNrm.xsd}VsDataContainer") # /{genericNrm.xsd}attributes/""{EricssonSpecificAttributes.xsd}vsDataNRCellDU")
            result = list(map(lambda p: self._5GvsDataNRCellDU(p, response_5g), DataContainers))
            result = list(map(lambda p: self._5GvsDataNRSectorCarrier(p, response_5g), DataContainers))
            # self.data.append(response_5g.copy())
        except Exception as e:
            print(f"An error occurred: {e}")


    def _5GvsDataNRCellDU(self, dataContainer, response_5g):
        try:
            if (self.getvalFromElem(dataContainer, 'xn', 'vsDataType') == "vsDataNRCellDU"):
                response_5g['cell_range'] = self.getvalFromElem(elem=dataContainer, namespace='es', key='cellRange')
                response_5g['nr_pci'] = self.getvalFromElem(elem=dataContainer, namespace='es', key='nRPCI')
                response_5g['cid'] = self.getvalFromElem(elem=dataContainer, namespace='es', key='cellLocalId')
                response_5g['cell_name'] = self.getvalFromElem(elem=dataContainer, namespace='es', key='nRCellDUId')
                # response_5g['container_id'] = dataContainer.get("id")
                # default values
                response_5g['ran_vendor'] = self.get_ran_vendor()
                response_5g['fiveg_overlapping_coverage'] = self.get_fiveg_overlapping_coverage()
                # response_5g['cell_type'] = self.get_cell_type()
                response_5g['region1'] = self.get_region1()
                response_5g['region2'] = self.cell_region[response_5g['cell_name'][:-1]][0]
                response_5g['region3'] = self.cell_region[response_5g['cell_name'][:-1]][1]
                response_5g['region4'] = self.cell_region[response_5g['cell_name'][:-1]][2]
                response_5g['sector'] = response_5g['cell_name'][-1]
                # response_5g['height'] = self.get_height()
                # response_5g['beam_width'] = self.get_beam_width()
                # response_5g['beam_direction'] = self.get_beam_direction()
                # response_5g['tilt'] = self.get_tilt()
                # response_5g['shared_cell'] = self.get_shared_cell()
                response_5g['nr_cell_id'] = self.nci_5g[response_5g['cell_name']]
                self.data.append(response_5g.copy())
            if (self.getvalFromElem(dataContainer, 'xn', 'vsDataType') == "vsDataNRCellCU"):
                nciid = dataContainer.get("id")
                nci = self.getvalFromElem(elem=dataContainer, namespace='es', key='nCI')
                self.nci_5g[nciid] = nci
        except Exception as e:
            print(f"An error occurred: {e}")


    def _5GvsDataNRSectorCarrier(self, dataContainer, response_5g):
        try:
            if (self.getvalFromElem(dataContainer, 'xn', 'vsDataType') == "vsDataNRSectorCarrier"):
                cell_name = dict(val.split('=') for val in self.getvalFromElem(dataContainer, 'es', 'reservedBy').split(','))['vsDataNRCellDU']
                key1 = 'nr_gnodeb_name'# 'meContext'
                key2 = 'cell_name'
                lat = self.getvalFromElem(dataContainer, 'es' ,'latitude')
                # print("lat1", lat)
                lat = self.lat_lon(lat) if lat else self.get_lat()
                # print("lat2", lat)
                lon = self.getvalFromElem(dataContainer, 'es' ,'longitude')
                lon = self.lat_lon(lon) if lon else self.get_lon()
                self.add_conditional_data(key1=key1, value1=response_5g[key1], key2=key2, value2=cell_name, key_add='lat',
                                        value_add=lat, data=self.data)
                self.add_conditional_data(key1=key1, value1=response_5g[key1], key2=key2, value2=cell_name, key_add='lon',
                                        value_add=lon, data=self.data)
                response_5g.pop(key2)
        except Exception as e:
            print(f"An error occurred: {e}")


    def _4GENodeBFunction(self, vsDataContainer, response_4g):
        try:
            eNodeBFunction = vsDataContainer.find("{genericNrm.xsd}attributes").find("{EricssonSpecificAttributes.xsd}vsDataENodeBFunction")
            if eNodeBFunction is not None:
                response_4g['mcc'] = self.getvalFromElem(eNodeBFunction, 'es', 'mcc')
                response_4g['mnc'] = self.getvalFromElem(eNodeBFunction, 'es', 'mnc')
                response_4g['lte_enodeb_id'] = self.getvalFromElem(eNodeBFunction, 'es', 'eNBId')
                DataContainers = vsDataContainer.findall("{genericNrm.xsd}VsDataContainer")
                eNodeBFunction.clear()
                result = list(map(lambda p: self._4GvsDataContainers(p, response_4g), DataContainers))
                # [self.vsDataContainers(p, response) for p in DataContainers]
                result = list(map(lambda p: self._4GvsDataSectorCarrier(p, response_4g), DataContainers))
                DataContainers.clear()
        except Exception as e:
            print(f"An error occurred: {e}")


    def _4GvsDataContainers(self, vsDataContainers, response_4g):
        # print(self.data)
        try:
            if (self.getvalFromElem(vsDataContainers, 'xn', 'vsDataType') == "vsDataEUtranCellFDD"):
                response_4g['cell_name'] = vsDataContainers.get("id")
                response_4g['cid'] = self.getvalFromElem(vsDataContainers, 'es' ,'cellId')
                lat = self.getvalFromElem(vsDataContainers, 'es' ,'latitude')
                response_4g['lat'] = self.lat_lon(lat) if lat else self.get_lat()
                lon = self.getvalFromElem(vsDataContainers, 'es' ,'longitude')
                response_4g['lon'] = self.lat_lon(lon) if lon else self.get_lon()
                response_4g['cell_range'] = self.getvalFromElem(vsDataContainers, 'es' ,'cellRange')
                response_4g['lte_tac'] = self.getvalFromElem(vsDataContainers, 'es' ,'tac')
                response_4g['lte_eci'] = 256* int(response_4g['lte_enodeb_id']) + int(response_4g['cid'])
                response_4g['ran_vendor'] = self.get_ran_vendor()
                response_4g['fiveg_overlapping_coverage'] = self.get_fiveg_overlapping_coverage()
                # response_4g['cell_type'] = self.get_cell_type()
                response_4g['region1'] = self.get_region1()
                response_4g['region2'] = self.cell_region[response_4g['cell_name'][:-1]][0]
                response_4g['region3'] = self.cell_region[response_4g['cell_name'][:-1]][1]
                response_4g['region4'] = self.cell_region[response_4g['cell_name'][:-1]][2]
                response_4g['sector'] = response_4g['cell_name'][-1]
                # response_4g['height'] = self.get_height()
                # response_4g['beam_width'] = self.get_beam_width()
                # response_4g['beam_direction'] = self.get_beam_direction()
                # response_4g['tilt'] = self.get_tilt()
                # response_4g['shared_cell'] = self.get_shared_cell()
                self.data.append(response_4g.copy())
        except Exception as e:
            print(f"An error occurred: {e}")


    def _4GvsDataSectorCarrier(self, vsDataContainers, response_4g):
        try:
            if (self.getvalFromElem(vsDataContainers, 'xn', 'vsDataType') == "vsDataSectorCarrier"):
                # response['sectorCarrierId'] = self.getvalFromElem(vsDataContainers, 'es' ,'sectorCarrierId')
                id = vsDataContainers.get("id")
                key1 = 'lte_enodeb_name'
                key2 = 'cell_name'
                #self.add_conditional_data(key1=key1, value1=response_4g[key1], key2=key2, value2=id, key_add='sectorCarrierId',
                #                        value_add=self.getvalFromElem(vsDataContainers, 'es' ,'sectorCarrierId'), data=self.data)
        except Exception as e:
            print(f"An error occurred: {e}")


    def lat_lon(self, l) -> str:
        return str("{:.6f}".format(float(l) / 1000000))

    def get_lat(self) -> str:
        # lat = ['49.1833', '49.1975', '49.1889', '49.1900', '49.2333']
        lat = ['0.0']
        return random.choice(lat)

    def get_lon(self) -> str:
        # lon = ['-2.1071', '-2.0167', '-2.1708', '-2.2000', '-2.2333']
        lon = ['0.0']
        return random.choice(lon)

    def get_ran_vendor(self):
        return 'Ericsson'

    def get_fiveg_overlapping_coverage(self):
        return 0

    def get_cell_type(self):
        cell_type = ['Indoor', 'Macro']
        # return random.choice(cell_type)
        return ''

    def get_beam_direction(self):
        return ''

    def get_region1(self):
        return 'Channel Islands'

    def get_height(self):
        return ''

    def get_beam_width(self):
        return ''

    def get_tilt(self):
        return ''

    def get_shared_cell(self):
        return ''
    
    def get_cell_region(self, csv_file):
        fieldnames = ("region2", "region3", "region4", "cell_name")
        d = '|'

        with open(csv_file, 'r') as csvfile:
            reader = csv.DictReader(f=csvfile, fieldnames=fieldnames, delimiter=d)

            for row in reader:
                key = row['cell_name'][:-1]
                value = [row['region2'], row['region3'], row['region4']]
                self.cell_region[key] = value

    def getvalFromElem(self, elem, namespace: str, key: str) -> str:
        return elem.find(".//" + namespace + ":" + key, namespaces={namespace: self.ns[namespace]}).text

    def getElemFromElem(self, elem, namespace: str, key: str) -> object:
        return elem.find(".//" + namespace + ":" + key, namespaces={namespace: self.ns[namespace]})

    def getAllFromElem(self, elem, namespace: str, key: str) -> object:
        ns = "{" + self.ns[namespace] + "}"
        return elem.findall(".//" + ns + key)

    def add_conditional_data(self, key1: str, value1: str, key2: str, value2: str, key_add: str, value_add: str, data: list) -> None:
        [d.update({key_add: value_add}) for d in self.data if d.get(key1) == value1 and d.get(key2) == value2]


