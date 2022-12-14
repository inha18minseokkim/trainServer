import FinanceDataReader as fdr
import asyncio
import numpy as np
import pandas
import requests
from bs4 import BeautifulSoup


class StkPrice:
    async def getPrice(self, code: str):
        res = fdr.DataReader(code)['Close']
        return res
    async def getPriceList(self,li : list):
        res = await asyncio.gather(*[self.getPrice(code) for code in li])
        #print(res)
        return res
    async def getMeanStd(self, code : str):
        price: pandas.Series = await self.getPrice(code)
        rateofreturn = price.apply(np.log) - price.apply(np.log).shift(20)
        #print(rateofreturn)
        rateofreturn.dropna(inplace=True)
        rateofreturn = np.array(rateofreturn)
        return [np.mean(rateofreturn),np.std(rateofreturn)]

    async def getMeanStdList(self, code : list):
        price: list(pandas.Series) = await self.getPriceList(code)
        li = []
        for df in price:
            tmpreturn = df.apply(np.log) - df.apply(np.log).shift(20)
            tmpreturn.dropna(inplace=True)
            tmpreturn = np.array(tmpreturn)
            li.append([np.mean(tmpreturn),np.std(tmpreturn)])
        return li
    def getKoreaBondRtn(self):
        # res = fdr.DataReader('KR1YT=RR')
        # print(res)
        # return res['Close'] / 100
        url = "https://finance.naver.com/marketindex/interestDetail.naver?marketindexCd=IRR_GOVT03Y#"
        response = requests.get(url)
        if response.status_code == 200:
            html = response.text
            # print(html)
            soup = BeautifulSoup(html, 'html.parser')
            rate = list(soup.select_one(".no_down"))
            rate = rate[1:-1]
            res = ''
            for i in rate:
                res += i.get_text()
            res = float(res)
            return res / 100
        else:
            return -1
    def getCov(self,code: list):
        pricedata: list = asyncio.run(self.getPriceList(code))
        df = pandas.DataFrame(pricedata).T
        df.columns = code
        monthly_rtn: pandas.DataFrame = (df - df.shift(25))/df.shift(25)
        monthly_rtn.dropna(inplace=True)
        rtn_cov = monthly_rtn.cov()
        return rtn_cov
if __name__ == "__main__":
    loader: StkPrice = StkPrice()
    #res = asyncio.run(loader.getMeanStdList(['005930','091160','091170']))
    #res = loader.getCov(['005930','091160','091170'])
    res = loader.getKoreaBondRtn()
    print(res)