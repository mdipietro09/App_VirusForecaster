
import pandas as pd
import numpy as np
from scipy import optimize
import matplotlib.pyplot as plt
import matplotlib.dates as pltdates
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
        
        
    def add_deaths(self, mortality):
        self.dtf_out["deaths"] = self.dtf_out[["data","forecast"]].apply(lambda x: 
                                 int(mortality*x[0]) if not np.isnan(x[0]) else int(mortality*x[1]), 
                                 axis=1)
        
    
    def plot(self, country):
        ## main plots
        fig, ax = plt.subplots(figsize=(15,10))
        ax.scatter(self.dtf_out.index, self.dtf_out["data"], color="black", label="data")
        ax.plot(self.dtf_out.index, self.dtf_out["forecast"], label="forecast")
        ## today vline
        ax.axvline(self.today, ls='--', color="black")
        ax.text(x=self.today, y=self.dtf_out["forecast"].max(), s="today", fontsize=15)
        ## fill under the curve
        ax.fill_between(self.dtf_out.index, self.dtf_out["forecast"], alpha=0.2)
        ## deaths
        ax.bar(self.dtf_out.index, self.dtf_out["deaths"], color="red", label="deaths")
        ## ax settings
        fig.suptitle(country+": Forecast for 30 days from today", fontsize=20)
        plt.xticks(rotation=70) 
        ax.grid(True)
        ax.legend(loc="upper left")
        ## save fig
        bytes_image = io.BytesIO()
        plt.savefig(bytes_image, format='png')
        bytes_image.seek(0)
        bytes_image_url = base64.b64encode(bytes_image.getvalue()).decode()
        return 'data:image/png;base64,{}'.format(bytes_image_url)
    
    
   