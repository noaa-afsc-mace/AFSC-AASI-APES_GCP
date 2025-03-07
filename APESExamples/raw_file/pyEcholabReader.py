import os                              
os.environ["CRYPTOGRAPHY_OPENSSL_NO_LEGACY"] ="yes"
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

def integrationTable(raw_files, cal_file=None, pulse='CW', interval_axis='ping_number', interval_length=50, 
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
    sv_chan_list = filterChannels(ek_data, mode='Active', pulse=pulse)
    
    # Get volume backscattering strength (Sv) data for filtered channels
    if pulse == 'FM':
        sv_data = echosounder.get_Svf(ek_data, cal_data, channel_ids=sv_chan_list)
    else:
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
    interval_col, layer_col, freq_col, sv_col = np.array([]), np.array([]),np.array([]),np.array([])
    
    # Collect integration results for all channels, intervals, and layers
    for channel in integrated_data.keys():
        # Get frequency for the channel (if consistent)
        if len(np.unique(sv_data[channel].frequency)) == 1:
            freq = np.unique(sv_data[channel].frequency)[0]
        else:
            freq = sv_data[channel].frequency
            
        # Iterate through all intervals and layers
        for interval in range(integrated_data[channel].mean_Sv.shape[0]):
            for layer in range(integrated_data[channel].mean_Sv.shape[1]):
                if pulse == 'FM':
                    interval_col = np.concatenate([interval_col,np.array([interval]*len(freq))])
                    layer_col = np.concatenate([layer_col,np.array([layer]*len(freq))])
                    freq_col = np.concatenate([freq_col, freq])
                    sv_col = np.concatenate([sv_col, integrated_data[channel].mean_Sv[interval, layer]])
                else:
                    # Append data to respective lists
                    interval_col = np.concatenate([interval_col, np.array([interval])])
                    layer_col = np.concatenate([layer_col, np.array([layer])])
                    freq_col = np.concatenate([freq_col, np.array([freq])])
                    sv_col = np.concatenate([sv_col,np.array([integrated_data[channel].mean_Sv[interval, layer]])])
    
    # Create DataFrame with integration results
    df = pd.DataFrame({'interval': interval_col, 
                         'layer': layer_col, 
                         'frequency': freq_col, 
                         'mean_Sv': sv_col})
    
    # If there are unequal layers (no bottom detected), balance the table by filling in NaNs
    df = balance_layers(df) 

    # return datafram
    return df

def balance_layers(df):
    """
    Balances a DataFrame to ensure all frequencies have the same number of layers.
    Only modifies the DataFrame if the frequencies have unequal numbers of layers.
    Adds new rows with NaN values in the 'mean_Sv' column where needed.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        Input DataFrame with columns: interval, layer, frequency, and sv
        
    Returns:
    --------
    pandas.DataFrame
        A balanced DataFrame where all frequencies have the same number of layers
    """
    # Check if all frequencies have the same number of unique layers
    layer_counts = df.groupby('frequency')['layer'].nunique()
    
    # If all frequencies already have the same number of layers, return the original dataframe
    if len(layer_counts.unique()) == 1:
        return df
    
    # Find the maximum number of layers per frequency
    max_layers_per_freq = df.groupby('frequency')['layer'].max()
    max_layers = max_layers_per_freq.max()
    
    # Create a new DataFrame to store the result
    result_df = pd.DataFrame(columns=df.columns)
    
    # For each frequency, add existing rows and then add missing layers with NaN sv values
    for freq in df['frequency'].unique():
        # Get existing data for this frequency
        freq_data = df[df['frequency'] == freq].copy()
        
        # Add existing rows to the result
        result_df = pd.concat([result_df, freq_data])
        
        # Find the max layer that exists for this frequency
        max_existing_layer = freq_data['layer'].max()
        
        # If this frequency already has the maximum number of layers, continue to next frequency
        if max_existing_layer == max_layers:
            continue
        
        # Get all unique intervals for this frequency
        intervals = freq_data['interval'].unique()
        
        # For each interval, add missing layers
        new_rows = []
        for interval in intervals:
            for layer in range(int(max_existing_layer) + 1, int(max_layers) + 1):
                # Create a new row with NaN for sv
                new_row = {
                    'interval': interval,
                    'frequency': freq,
                    'layer': layer,
                    'mean_Sv': np.nan
                }
                new_rows.append(new_row)
        
        # Add all new rows at once (more efficient)
        if new_rows:
            new_rows_df = pd.DataFrame(new_rows)
            result_df = pd.concat([result_df, new_rows_df])
    
    # Sort the resulting DataFrame for better organization
    result_df = result_df.sort_values(by=['frequency', 'interval', 'layer'])
    
    # Reset index for clean output
    result_df = result_df.reset_index(drop=True)
    
    return result_df


def download_raw_file_from_ncei(file_name, file_type, ship_name, survey_name, echosounder, data_source, file_download_directory):

    import boto3, botocore
    from botocore import UNSIGNED
    from botocore.client import Config
    import os


    s3 = boto3.resource(
    's3',
    aws_access_key_id='',
    aws_secret_access_key='',
    config=Config(signature_version=UNSIGNED)
        )

    BUCKET = 'noaa-wcsd-pds'

    if echosounder == "EK80":
        bot_file = file_name[:-3]+'xyz'
    elif echosounder == "EK60":
        bot_file = file_name[:-3]+'bot'
        
    try:
        for file in [file_name, bot_file]:
            if file not in os.listdir(file_download_directory): 
                print(file)
                s3.Bucket(BUCKET).download_file(os.sep.join(['data',file_type,ship_name,survey_name,echosounder]) +'/'+ file, file_download_directory+'/'+file)
                print('downloaded:', file)
            else:
                print('already found:', file)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
        else:
            raise
    
    return file_download_directory + file_name