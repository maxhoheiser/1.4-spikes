import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class BehaviorAnalysis():
    """[behaviour analysis class for phenosys Behavior Recording and Neuron Electrophysiology Recording]
    """    
    def __init__(self, sync_obj, deselect_trials=[]):
        """[summary]

        Args:
            session ([type]): [description]
            folder ([type]): [description]
            combined (pd): pandas datafame containing all the session information, from sync_class
        """        
        self.session = sync_obj.session
        self.folder = sync_obj.folder
        self.combined_df = sync_obj.combined_df
        self.gamble_side = sync_obj.gamble_side
        self.deselect_trials = deselect_trials

        self.all_trials_df = sync_obj.all_trials_df
        self.good_trials_df = sync_obj.good_trials_df

        for a,b in deselect_trials:
            if b == 'end':
                self.good_trials_df.loc[a:,'select'] = False
            else:
                self.good_trials_df.loc[a:b,'select'] = False

        self.selected_trials_df = self.good_trials_df.loc[self.good_trials_df['select'],:]
        self.selected_trials_df.reset_index(drop=True,inplace=True)

    def get_wheel_and_resp(self):
        wheel = []
        response = []
        working = self.combined.copy()
        working.reset_index(inplace=True)
        for index, row in working.iterrows():
            if index+4 == working.shape[0]:
                break 
            if (row['CSV Event'] == 'start') & ( (working.loc[index+1,'CSV Event'])=='wheel not stopping'):
                wheel.append(1)
                response.append(0)
            elif (row['CSV Event'] == 'start') & ( (working.loc[index+4,'CSV Event']) == 'no response in time'):
                response.append(1)
                wheel.append(0)
            elif (row['CSV Event'] == 'start') and ( ((working.loc[index+1,'CSV Event'])!='wheel not stopping') or  ((working.loc[index+4,'CSV Event']) != 'no response in time') ):
                wheel.append(0)
                response.append(0)
        
        self.behav_df = pd.DataFrame({'resp':response, 'wheel':wheel})
        # add rolling average
        resp_rol_df = pd.DataFrame(self.behav_df.resp.rolling(window=10).mean())
        resp_rol_df.fillna(0, inplace=True)
        wheel_rol_df = pd.DataFrame(self.behav_df.wheel.rolling(window=10).mean())
        wheel_rol_df.fillna(0, inplace=True)
        # add to dataframe
        self.behav_df['resp_rol']=resp_rol_df.values
        self.behav_df['wheel_rol']=wheel_rol_df.values

        return self.behav_df

    def plot_wheel_resp(self, wheel=True, resp=False, legend=False):
        if not 'behav_df' in dir(self):
            self.get_wheel_and_resp()
        plt.figure(figsize=(9, 4))
        if wheel:
            plt.plot(self.behav_df.wheel_rol, label='wheel not stopping')
        if resp:
            plt.plot(self.behav_df.resp_rol, label='no response in time')
        if legend:
            plt.legend(loc=(0.02, 0.1))
        plt.ylabel('rolling average (10)')
        plt.xlabel('trial')
        plt.show()
        