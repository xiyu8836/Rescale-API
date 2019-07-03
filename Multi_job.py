#!/usr/bin/python

import requests
import json
import time
import RescaleAPI
import pprint
import csv
api_key='bd2128efa577985cd87a4c338415ef3c059e1559'
api_url='https://platform.rescale.com'
rescale_system=RescaleAPI.RescaleAPI(api_key,api_url)
input_file='multi_job_input.csv'

#-----------------------------------------------------------------------------------------------------------------------
# User input information
num_job=0
job_name        =  []
core_name       =  []                       # this is core name instead of core code
analysis_name   =  []            # this is analysis name, instead of analysis code
version         =  []                      # has to be version code
file_name_list  =  []
license         =  []
command         =  []
cores           =  []
slots           =  []
with open(input_file,'rb') as csvfile:
    lines=csv.DictReader(csvfile)
    for row in lines:
        num_job=num_job+1
        job_name.append(row['job_name'])
        core_name.append(row['core_name'])
        analysis_name.append(row['analysis_name'])
        version.append(row['version'])
        file_name_list.append(row['input_file'].split(';'))
        license.append(bool(row['license']))
        command.append(row['command'])
        cores.append(int(row['cores']))
        slots.append(int(row['slots']))

#num_job=5
'''
job_name        =  ["LS-DYNA for API class1",
                    "LS-DYNA for API class2",
                    "LS-DYNA for API class3",
                    "LS-DYNA for API class4",
                    "LS-DYNA for API class5"
                    ]
core_name       =  ["Onyx","Nickel","Onyx","Nickel","Onyx"]                       # this is core name instead of core code
analysis_name   =  ["LS-DYNA","LS-DYNA","LS-DYNA","LS-DYNA","LS-DYNA"]            # this is analysis name, instead of analysis code
version         =  ["9.0.0","9.0.0","9.0.0","9.0.0","9.0.0"]                      # has to be version code
file_name_list  =  [["input.zip"],["input.zip"],["input.zip"],["input.zip"],["input.zip"]]
license         =  [True,True,True,True,True]
command         =  ["ls-dyna -n 2 -i neon.refined.rev01.k -p single",
                    "ls-dyna -n 2 -i neon.refined.rev01.k -p single",
                    "ls-dyna -n 2 -i neon.refined.rev01.k -p single",
                    "ls-dyna -n 2 -i neon.refined.rev01.k -p single",
                    "ls-dyna -n 2 -i neon.refined.rev01.k -p single"]
cores           =  [2,2,2,2,2]
slots           =  [1,1,1,1,1]
'''
#-----------------------------------------------------------------------------------------------------------------------
# This part is checking input parameters, no need to modify
for index in range(num_job):
    core_code=rescale_system.get_core_code(core_name=core_name[index])

    found_analysis=rescale_system.get_analysis(analysis_name=analysis_name[index])

    analysis_code=found_analysis["code"]

    rescale_system.check_analysis_version(found_analysis=found_analysis,version=version[index],core_code=core_code)

    file_uploaded=rescale_system.direct_upload_file(file_name_list=file_name_list[index])


#-----------------------------------------------------------------------------------------------------------------------
# Create and submit jobs
    job_id=rescale_system.create_job(job_name=job_name[index],license=license[index],command=command[index],analysis_code=analysis_code,
                                 versionCode=version[index],cores=cores[index],slots=slots[index],coretype=core_code,input_file=file_uploaded)
    rescale_system.submit_job(job_ID=job_id)



#-----------------------------------------------------------------------------------------------------------------------
# Monitor job status and start the second job
'''
complete=rescale_system.monitor_job_completion(job_ID=job_id)

if complete==True:
    job_id2 = rescale_system.create_job(job_name=job_name, license=license, command=command, analysis_code=analysis_code,
                                       versionCode=version, cores=cores, slots=slots, coretype=core_code,
                                       input_file=file_uploaded)
    rescale_system.submit_job(job_ID=job_id2)
'''
