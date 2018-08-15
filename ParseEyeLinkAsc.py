# ParseEyeLinkAsc.py
# - Reads in .asc data files from EyeLink and produces pandas dataframes for further analysis
#
# Created 7/31/18-8/15/18 by DJ.


def ParseEyeLinkAsc(elFilename):
    # dfTrial,dfMsg,dfFix,dfSacc,dfBlink,dfSamples = ParseEyeLinkAsc(elFilename)
    # -Reads in data files from EyeLink .asc file and produces readable dataframes for further analysis.
    #
    # INPUTS:
    # -elFilename is a string indicating an EyeLink data file from an AX-CPT task in the current path.
    #
    # OUTPUTS:
    # -dfTrial contains information about trials
    # -dfMsg contains information about messages (usually sent from stimulus software)
    # -dfFix contains information about fixations
    # -dfSacc contains information about saccades
    # -dfBlink contains information about blinks
    # -dfSamples contains information about individual samples
    #
    # Created 7/31/18-8/15/18 by DJ.
    
    # Import packages
    import numpy as np
    import pandas as pd
    import time

    # ===== READ IN FILES ===== #
    # Read in EyeLink file
    print('Reading in EyeLink file %s...'%elFilename)
    t = time.time()
    f = open(elFilename,'r')
    fileTxt0 = f.read().split("\n") # split into lines (runs)
    fileTxt0 = filter(None, fileTxt0) #  remove emptys
    fileTxt0 = np.array(fileTxt0) # concert to np array for simpler indexing
    f.close()
    print('Done! Took %f seconds.'%(time.time()-t))

    # Separate lines into samples and messages
    print('Sorting lines...')
    nLines = len(fileTxt0)
    lineType = np.array(['OTHER']*nLines,dtype='object')
    iStartRec = None
    t = time.time()
    for iLine in range(nLines):
        if len(fileTxt0[iLine])<3:
            lineType[iLine] = 'EMPTY'
        elif fileTxt0[iLine].startswith('*') or fileTxt0[iLine].startswith('>>>>>'):
            lineType[iLine] = 'COMMENT'
        elif fileTxt0[iLine].split()[0][0].isdigit() or fileTxt0[iLine].split()[0].startswith('-'):
            lineType[iLine] = 'SAMPLE'
        else:
            lineType[iLine] = fileTxt0[iLine].split()[0]
        if '!CAL' in fileTxt0[iLine]: # TODO: Find more general way of determining if recording has started
            iStartRec = iLine+1
    print('Done! Took %f seconds.'%(time.time()-t))
    
    
    
    # ===== PARSE EYELINK FILE ===== #
    t = time.time()
    # Trials
    print('Parsing trial markers...')
    iNotStart = np.nonzero(lineType!='START')[0]
    dfTrialStart = pd.read_csv(elFilename,skiprows=iNotStart,header=None,delim_whitespace=True,usecols=[1])
    dfTrialStart.columns = ['tStart']
    iNotEnd = np.nonzero(lineType!='END')[0]
    dfTrialEnd = pd.read_csv(elFilename,skiprows=iNotEnd,header=None,delim_whitespace=True,usecols=[1,5,6])
    dfTrialEnd.columns = ['tEnd','xRes','yRes']
    # combine trial info
    dfTrial = pd.concat([dfTrialStart,dfTrialEnd],axis=1)
    nTrials = dfTrial.shape[0]
    print('%d trials found.'%nTrials)

    # Import Messages
    print('Parsing stimulus messages...')
    t = time.time()
    iMsg = np.nonzero(lineType=='MSG')[0]
    # set up
    tMsg = []
    txtMsg = []
    t = time.time()
    for i in range(len(iMsg)):
        # separate MSG prefix and timestamp from rest of message
        info = fileTxt0[iMsg[i]].split()
        # extract info
        tMsg.append(int(info[1]))
        txtMsg.append(' '.join(info[2:]))
    # Convert dict to dataframe
    dfMsg = pd.DataFrame({'time':tMsg, 'text':txtMsg})
    print('Done! Took %f seconds.'%(time.time()-t))
    
    # Import Fixations
    print('Parsing fixations...')
    t = time.time()
    iNotEfix = np.nonzero(lineType!='EFIX')[0]
    dfFix = pd.read_csv(elFilename,skiprows=iNotEfix,header=None,delim_whitespace=True,usecols=range(1,8))
    dfFix.columns = ['eye','tStart','tEnd','duration','xAvg','yAvg','pupilAvg']
    nFix = dfFix.shape[0]
    print('Done! Took %f seconds.'%(time.time()-t))

    # Saccades
    print('Parsing saccades...')
    t = time.time()
    iNotEsacc = np.nonzero(lineType!='ESACC')[0]
    dfSacc = pd.read_csv(elFilename,skiprows=iNotEsacc,header=None,delim_whitespace=True,usecols=range(1,11))
    dfSacc.columns = ['eye','tStart','tEnd','duration','xStart','yStart','xEnd','yEnd','ampDeg','vPeak']
    print('Done! Took %f seconds.'%(time.time()-t))
    
    # Blinks
    print('Parsing blinks...')
    iNotEblink = np.nonzero(lineType!='EBLINK')[0]
    dfBlink = pd.read_csv(elFilename,skiprows=iNotEblink,header=None,delim_whitespace=True,usecols=range(1,5))
    dfBlink.columns = ['eye','tStart','tEnd','duration']
    print('Done! Took %f seconds.'%(time.time()-t))
    
    # Import samples
    print('Parsing samples...')
    t = time.time()
    iNotSample = np.nonzero( np.logical_or(lineType!='SAMPLE', np.arange(nLines)<iStartRec))[0]
    dfSamples = pd.read_csv(elFilename,skiprows=iNotSample,header=None,delim_whitespace=True,usecols=range(0,7))
    dfSamples.columns = ['tSample', 'LX', 'LY', 'LPupil', 'RX', 'RY', 'RPupil']
    # Convert values to numbers
    dfSamples['LX'] = pd.to_numeric(dfSamples['LX'],errors='coerce')
    dfSamples['LY'] = pd.to_numeric(dfSamples['LY'],errors='coerce')
    dfSamples['RX'] = pd.to_numeric(dfSamples['RX'],errors='coerce')
    dfSamples['RY'] = pd.to_numeric(dfSamples['RY'],errors='coerce')
    print('Done! Took %.1f seconds.'%(time.time()-t))
    
    # Return new compilation dataframe
    return dfTrial,dfMsg,dfFix,dfSacc,dfBlink,dfSamples
    
    
    
