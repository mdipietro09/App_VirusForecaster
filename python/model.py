
import pandas as pd
import numpy as np
from scipy import optimize



class Model():
    
    def __init__(self, dtf):
        self.dtf = dtf
        
    
    @staticmethod
    def f(X, c, k, m):
        y = c / (1 + np.exp(-k*(X-m)))
        return y
    
    
    @staticmethod
    def fit_parametric(X, y, f, p0):
        model, cov = optimize.curve_fit(f, X, y, maxfev=10000, p0=p0)
        return model
    
    
    @staticmethod
    def forecast_parametric(model, f, X):
        preds = f(X, model[0], model[1], model[2])
        return preds
    
    
    @staticmethod
    def generate_indexdate(start):
        index = pd.date_range(start=start, periods=30, freq="D")
        index = index[1:]
        return index
    
    
    @staticmethod
    def add_diff(dtf):
        ## create delta columns
        dtf["delta_data"] = dtf["data"] - dtf["data"].shift(1)
        dtf["delta_forecast"] = dtf["forecast"] - dtf["forecast"].shift(1)
        
        ## fill Nas
        dtf["delta_data"] = dtf["delta_data"].fillna(method='bfill')
        dtf["delta_forecast"] = dtf["delta_forecast"].fillna(method='bfill')
        
        ## interpolate outlier
        idx = dtf[pd.isnull(dtf["data"])]["delta_forecast"].index[0]
        posx = dtf.index.tolist().index(idx)
        posx_a = posx - 1
        posx_b = posx + 1
        dtf["delta_forecast"].iloc[posx] = (dtf["delta_forecast"].iloc[posx_a] + dtf["delta_forecast"].iloc[posx_b])/2
        return dtf

    
    def forecast(self):
        ## fit
        y = self.dtf["data"].values
        t = np.arange(len(y))
        model = self.fit_parametric(t, y, self.f, p0=[np.max(y), 1, 1])
        fitted = self.f(t, model[0], model[1], model[2])
        self.dtf["forecast"] = fitted
        
        ## forecast
        t_ahead = np.arange(len(y)+1, len(y)+30)
        forecast = self.forecast_parametric(model, self.f, t_ahead)
        
        ## create dtf
        self.today = self.dtf.index[-1]
        idxdates = self.generate_indexdate(start=self.today)
        preds = pd.DataFrame(data=forecast, index=idxdates, columns=["forecast"])
        self.dtf = self.dtf.append(preds)
        
        ## add diff
        self.dtf = self.add_diff(self.dtf)
                
        
    def add_deaths(self, mortality):
        self.dtf["deaths"] = self.dtf[["deaths","forecast"]].apply(lambda x: 
                             mortality*x[1] if np.isnan(x[0]) else x[0], 
                             axis=1)