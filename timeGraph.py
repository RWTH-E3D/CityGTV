'''
Draw time-number_of_building graph

'''

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def main():
    # change the font size here if needed
    plt.rcParams.update({'font.size': 20})

    # using Excel file
    df = pd.read_excel("timeData.xlsx",header=0)

    n = np.array(df.iloc[:,0])
    print("n=",n)
    t_nmp = np.array(df.iloc[:,1])
    print("t_nmp=",t_nmp)
    t_mp = np.array(df.iloc[:,2])
    print("t_mp=",t_mp)

    #ratio = np.array(df.iloc[:,3])
    #print("ratio=",ratio)

    myDPI = 600
    fig = plt.figure(dpi=myDPI, figsize=(16,9))
    ax1 = fig.add_subplot(111)

    ax1.plot(n, t_nmp, 'darkorange',label='Non-multiprocessing',marker='o')

    ax1.plot(n, t_mp, 'navy',label='Multiprocessing',marker='o')

    #ax1.plot(n, ratio, 'orangered', label='Ratio: Non-MP to MP')

    # Labels
    ax1.set_xlabel('Number of Buildings')
    ax1.set_ylabel('Transformation Time(s)')
    ax1.legend(fontsize = 'x-large')

    plt.savefig("MP_vs_NMP_time-number_of_building_GRAPH.png")
if __name__ == '__main__':
    main()


    