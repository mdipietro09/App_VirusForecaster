
import pandas as pd
import numpy as np
from scipy import optimize
import matplotlib.pyplot as plt
import matplotlib as mplt
import io
import base64



class model():
    
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
        dtf["delta_data"] = dtf["data"] - dtf["data"].shift(1)
        dtf["delta_forecast"] = dtf["forecast"] - dtf["forecast"].shift(1)
        idx = dtf[pd.isnull(dtf["data"])]["delta_forecast"].index[0]
        posx = dtf.index.tolist().index(idx)
        posx_a = posx - 1
        posx_b = posx + 1
        dtf["delta_forecast"].iloc[posx] = (dtf["delta_forecast"].iloc[posx_a] + dtf["delta_forecast"].iloc[posx_b])/2
        return dtf

    
    def forecast(self, cases):
        ## fit
        y = cases["data"].values
        t = np.arange(len(y))
        model = self.fit_parametric(t, y, self.f, p0=[np.max(y), 1, 1])
        fitted = self.f(t, model[0], model[1], model[2])
        cases["forecast"] = fitted
        
        ## forecast
        t_ahead = np.arange(len(y)+1, len(y)+30)
        forecast = self.forecast_parametric(model, self.f, t_ahead)
        
        ## create dtf
        self.today = cases.index[-1]
        idxdates = self.generate_indexdate(start=self.today)
        preds = pd.DataFrame(data=forecast, index=idxdates, columns=["forecast"])
        self.dtf_out = cases.append(preds)
        
        ## add diff
        self.dtf_out = self.add_diff(self.dtf_out)
                
        
    def add_deaths(self, mortality):
        self.dtf_out["deaths"] = self.dtf_out[["deaths","forecast"]].apply(lambda x: 
                                 mortality*x[1] if np.isnan(x[0]) else x[0], 
                                 axis=1)        
        

    def plot(self, country):
        fig, ax = plt.subplots(nrows=2, ncols=1, sharex=True, figsize=(15,10))
        
        ## 1st plot
        ### main plots
        ax[0].scatter(self.dtf_out.index, self.dtf_out["data"], color="black", label="data")
        ax[0].plot(self.dtf_out.index, self.dtf_out["forecast"], label="forecast")
        ### today vline
        ax[0].axvline(self.today, ls='--', color="black")
        ax[0].text(x=self.today, y=self.dtf_out["forecast"].max(), s="today", fontsize=15)
        ### fill under the curve
        ax[0].fill_between(self.dtf_out.index, self.dtf_out["forecast"], alpha=0.2)
        ### deaths
        ax[0].bar(self.dtf_out.index, self.dtf_out["deaths"], color="red", label="deaths")
        ### ax settings
        fig.suptitle(country+": Forecast for 30 days from today", fontsize=20)
        ax[0].set_title("Cases: "+"{:,}".format(int(self.dtf_out["forecast"].max()))+
                        "      Deaths: "+"{:,}".format(int(self.dtf_out["deaths"].max())))
        ax[0].yaxis.set_major_formatter(mplt.ticker.StrMethodFormatter('{x:,.0f}'))
        ax[0].grid(True)
        ax[0].legend(loc="upper left")
        
        ## 2nd plot
        ### main plots
        ax[1].bar(self.dtf_out.index, self.dtf_out["delta_data"], color="black", alpha=0.7)
        ax[1].plot(self.dtf_out.index, self.dtf_out["delta_forecast"])        
        ### today vline
        ax[1].axvline(self.today, ls='--', color="black")
        ### fill under the curve
        ax[1].fill_between(self.dtf_out.index, self.dtf_out["delta_forecast"], alpha=0.2)
        ### ax settings
        ax[1].set_title("New Cases")
        ax[1].yaxis.set_major_formatter(mplt.ticker.StrMethodFormatter('{x:,.0f}'))
        ax[1].grid(True)
        
        ## save fig
        bytes_image = io.BytesIO()
        plt.savefig(bytes_image, format='png')
        bytes_image.seek(0)
        bytes_image_url = base64.b64encode(bytes_image.getvalue()).decode()
        return 'data:image/png;base64,{}'.format(bytes_image_url)
    
    
   