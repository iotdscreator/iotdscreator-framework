# Features Extracted by IoTDSCreator
IoTDSCreator generates four types of datasets including:
 - packet dataset (19 features): it contains features extracted from each packet captured from a vantage points, with its label.
 - flow dataset (41 features): it contains features extracted from the relationship between packets within a window, which is defined by a starting timestamp with a window length.
 - host dataset (40 features): it contains features extracted from each atop result sent from each host.
 - transition dataset (67 features): it contains features extracted from the relationship between resource usage reported within a window, which is defined by a starting timestamp with a window length.

Details of features are listed in each directory.
