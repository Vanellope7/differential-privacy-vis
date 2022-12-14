import json

import numpy as np
from django.http import JsonResponse

from RiskTree.Class import JsonEncoder
from tools.df_processor import DFProcessor
from tools.Laplace import Laplace
from tools.utils import laplace_P


def GetNoisyDataDistribution(request):
    postData = json.loads(request.body)
    dfp = DFProcessor(postData['FileName'], postData['QueryAttr'],
                      postData['QueryCondition'], postData['sensitivityWay'], postData['Interval'])
    res = eval("dfp.{0}()".format(postData['QueryType']))
    sensitivity = dfp.getSensitivity(postData['QueryType'])
    b = sensitivity / postData['epsilon']
    L = Laplace(b)
    D = []
    for x in np.linspace(-sensitivity * 2, sensitivity * 2, 1000):
        D.append([x + res, L.laplace_f(x)])
    return JsonResponse({'distribution': D, 'b': b, 'sensitivity': sensitivity, 'ExactVal': res}, encoder=JsonEncoder)


def GetPrivacyDistribution(request):
    postData = json.loads(request.body)
    b = postData['b']
    targetResult = postData['targetResult']
    L = Laplace(b)
    D = []
    for x in np.linspace(-5 * targetResult, 5 * targetResult, 1000):
        D.append([x + targetResult, L.Laplace_DV_f(x)])
    return JsonResponse({'distribution': D})


def GetOppositeProbability(request):
    postData = json.loads(request.body)
    b = postData['b']
    interval = postData['interval']
    ExactVal = postData['ExactVal']
    privacy = ExactVal['firstQuery'] - ExactVal['secondQuery']
    domainDeviation = postData['domainDeviation']

    firstRes, secondRes = [], []
    for x in np.linspace(-domainDeviation, domainDeviation, 1000):
        firstRes.append([x + ExactVal['firstQuery'], laplace_P([x + privacy - interval[1], x + privacy - interval[0]], b)])
        secondRes.append([x + ExactVal['secondQuery'], laplace_P([x - privacy + interval[0], x - privacy + interval[1]], b)])
    return JsonResponse({'firstRes': firstRes, 'secondRes': secondRes})

