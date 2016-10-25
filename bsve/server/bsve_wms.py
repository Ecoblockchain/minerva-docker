import json

from bsve_wms_styles import BsveWmsStyle
from girder.api import access
from girder.api.describe import Description
from girder.plugins.minerva.rest.dataset import Dataset
from girder.plugins.minerva.utility.cookie import getExtraHeaders

import requests


class BsveWmsDataset(Dataset):

    def __init__(self):
        self.resourceName = 'bsve_datasets_wms'
        self.route('POST', (), self.createBsveSource)

    @access.user
    def createBsveSource(self, params):
        """ Hits the bsve urls """

        # Bsve geoserver (wms get capabilities url)
        wms = "https://api-qa.bsvecosystem.net/data/v2/" + \
              "sources/geotiles/meta/list"

        resp = requests.get(wms, headers=getExtraHeaders())
        data = json.loads(resp.text)

        layers = []

        for d in data['tiles']:
            wms_params = {}
            wms_params['typeName'] = d['name']
            wms_params['name'] = d['styles'][0]['title']
            wms_params['abstract'] = d['abstract']
            wms_params['source'] = {'layer_source': 'Reference',
                                    'source_type': 'wms'}
            wms_params['geo_render'] = {'type': 'wms'}
            layer_type = 'raster' if 'WCS' in d['keywords'] else 'vector'
            dataset = self.createBsveDataset(wms_params, layer_type)
            layers.append(dataset)

        return layers

    @access.user
    def createBsveDataset(self, params, layer_type):
        typeName = params['typeName']

        try:
            layer_info = BsveWmsStyle(typeName).get_layer_info(layer_type)
        except TypeError:
            layer_info = ""

        # TODO: Add the legend url here once it is
        # ready on bsve side
        self.requireParams(('name'), params)
        name = params['name']

        params['layer_info'] = layer_info
        params['adapter'] = 'bsve'

        dataset = self.constructDataset(name, params)
        return dataset

    createBsveSource.description = (
        Description('Create bsve datasets from bsve geoserver')
    )
