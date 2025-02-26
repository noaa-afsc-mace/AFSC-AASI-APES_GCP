import os                              
from echolab2.instruments import echosounder  
from echolab2.processing import grid, integration, line 
import numpy as np                     
from glob import glob                 
import pandas as pd                  

def fileList(fl, fext):
    """
    Process file inputs and return a list of files to be processed.
    
    Parameters:
        fl (str): File path or directory path
        fext (str): File extension to look for
        
    Returns:
        list: List of file paths
    """
    if os.path.isfile(fl):
        print('Processing a single raw file')
    elif os.path.isdir(fl):
        fl = glob(fl+'*.'+fext)  # Get all files with the specified extension in the directory
        print('Found %i %s files' % (len(fl), fext))
    else:
        raise ValueError(f"Unsupported path/file type: {fl}")
    return fl

def add_channel_dictionary(ek_data):
    """
    Create a dictionary of channel information including mode (Active/Passive) and pulse type (FM/CW).
    
    Parameters:
        ek_data: Echosounder data object
        
    Returns:
        ek_data: Updated echosounder data object with added dictionary
    """
    ek_dict = {}
    for channel in ek_data.channel_ids:
        # Determine if channel is passive or active
        if ek_data.get_channel_data()[channel][0].is_passive():
            mode = 'Passive'
        else:
            mode = 'Active'
        
        # Determine if pulse is frequency modulated or continuous wave
        if ek_data.get_channel_data()[channel][0].is_fm():
            pulse = 'FM'
        else:
            pulse = 'CW'
        
        # Store channel information in dictionary
        ek_dict[channel] = {'Mode': mode, 'Pulse': pulse}
    
    # Add dictionary to echosounder data object
    ek_data.ek_dict = ek_dict
    return ek_data

def filterChannels(ek_data, mode='Active', pulse='CW'):
    """
    Filter channels based on mode and pulse type.
    
    Parameters:
        ek_data: Echosounder data object
        mode (str): Mode to filter by (default 'Active')
        pulse (str): Pulse type to filter by (default 'CW')
        
    Returns:
        list: List of channel IDs that match the filter criteria
    """
    channels = []
    for channel in ek_data.channel_ids:
        if ek_data.ek_dict[channel]['Mode'] == mode and ek_data.ek_dict[channel]['Pulse'] == pulse:
            channels.append(channel)
    return channels

def integrationTable(raw_files, cal_file=None, interval_axis='ping_number', interval_length=50, 
                     layer_axis='range', layer_thickness=5, surf_offset=2, bot_offset=0.5):
    """
    Create an integration table from echosounder data.
    
    Parameters:
        raw_files (str): Path to raw files or directory containing raw files
        cal_file (str): Path to calibration file or directory (optional)
        interval_axis (str): Axis to use for integration intervals (default 'ping_number')
        interval_length (int): Length of integration intervals (default 50)
        layer_axis (str): Axis to use for integration layers (default 'range')
        layer_thickness (int): Thickness of integration layers (default 5)
        surf_offset (float/int/str): Surface exclusion offset (default 2)
        bot_offset (float): Bottom exclusion offset (default 0.5)
        
    Returns:
        pandas.DataFrame: DataFrame containing integration results
    """
    # Get list of raw files
    raw_file = fileList(raw_files, 'raw')
    
    # Read echosounder data
    ek_data = echosounder.read(raw_file)
    
    # Add channel dictionary with mode and pulse information
    ek_data = add_channel_dictionary(ek_data)
    
    # Try to get calibration data from XML file, otherwise get from raw file
    try:
        cal_file = fileList(cal_file, 'xml')
        cal_data = echosounder.get_calibration_from_xml(ek_data, cal_file)
    except:
        cal_data = echosounder.get_calibration_from_raw(ek_data)
    
    # Filter for active channels with continuous wave (CW) pulse
    sv_chan_list = filterChannels(ek_data, mode='Active', pulse='CW')
    
    # Get volume backscattering strength (Sv) data for filtered channels
    sv_data = echosounder.get_Sv(ek_data, cal_data, channel_ids=sv_chan_list)
    
    # Initialize dictionary to store integration results
    integrated_data = {}
    
    # Process each channel
    for channel in sv_data.keys():
        # Initialize integrator without minimum threshold
        i = integration.integrator(min_threshold_applied=False)
        
        # Initialize grid for integration
        g = grid.grid(interval_length=interval_length, interval_axis=interval_axis,
                     layer_axis=layer_axis, layer_thickness=layer_thickness,
                     data=sv_data[channel])
        
        # Handle surface exclusion line based on surf_offset parameter
        if isinstance(surf_offset, int) | isinstance(surf_offset, float):
            # If surf_offset is a number, create a constant line at that depth
            exclude_above_line = line.line(ping_time=sv_data[channel].ping_time, data=surf_offset)
        elif surf_offset == 'xyz':
            # If surf_offset is 'xyz', use top_xyz from inputs (not defined in this code snippet)
            exclude_above_line = inputs.top_xyz
        
        # Perform integration, with or without bottom line exclusion
        if hasattr(sv_data[channel], 'bottom_line'):
            # If bottom line exists, exclude data below it minus the offset
            integrated_data[channel] = i.integrate(sv_data[channel], g, 
                                                 exclude_above_line=exclude_above_line,
                                                 exclude_below_line=sv_data[channel].bottom_line-bot_offset) 
        else:
            # If no bottom line, only exclude data above the surface line
            integrated_data[channel] = i.integrate(sv_data[channel], g, 
                                                 exclude_above_line=exclude_above_line)
    
    # Initialize lists to store data for the DataFrame
    interval_col, layer_col, freq_col, sv_col = [], [], [], []
    
    # Collect integration results for all channels, intervals, and layers
    for channel in integrated_data.keys():
        # Get frequency for the channel (if consistent)
        if len(np.unique(ek_data.get_channel_data()[channel][0].frequency)) == 1:
            freq = ek_data.get_channel_data()[channel][0].frequency[0]
        else:
            freq = None
            
        # Iterate through all intervals and layers
        for interval in range(integrated_data[channel].mean_Sv.shape[0]):
            for layer in range(integrated_data[channel].mean_Sv.shape[1]):
                # Append data to respective lists
                interval_col.append(interval)
                layer_col.append(layer)
                freq_col.append(freq)
                sv_col.append(integrated_data[channel].mean_Sv[interval, layer])
    
    # Create and return DataFrame with integration results
    return pd.DataFrame({'interval': interval_col, 
                         'layer': layer_col, 
                         'frequency': freq_col, 
                         'mean_Sv': sv_col})