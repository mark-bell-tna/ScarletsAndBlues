#!/usr/bin/python3

from sandb_data_reader import sandbDataReader

workflow = "People"

#data_file_name = "scarlets-and-blues-classifications.csv"
data_files = {"Meetings": "meetings-classifications.csv",
              "People": "../Data/people-classifications.csv"}

data_file_name = data_files[workflow]

SDR = sandbDataReader()
SDR.load_data(data_file_name, workflow, version=56.83)

for R in SDR(iter_min=5,iter_max=5):
    #print(R)
    #data_file = open("ImageData/" + R[0] + ".csv", "w")
    users = set()
    for row_id in R[1]:
        u = SDR.get_row_by_id(row_id).get_by_key('user_name')
        users.add(u)
    if len(users) != len(R[1]):
        print("Skipping:", R[0])
        continue  # duplicate user for annotations
    print(R)
    
    
