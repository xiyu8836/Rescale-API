#!/usr/bin/python

import requests
import json
import time
import RescaleAPI
import pprint

api_key='bd2128efa577985cd87a4c338415ef3c059e1559'
api_url='https://platform.rescale.com'
rescale_system=RescaleAPI.RescaleAPI(api_key,api_url)

#-----------------------------------------------------------------------------------------------------------------------
# User input information
job_name        =  "LS-DYNA for API class"
core_name       =  "Onyx"                       # this is core name instead of core code
analysis_name   =  "LS-DYNA"                    # this is analysis name, instead of analysis code
version         =  "9.0.0"                      # has to be version code
file_name_list  =  ["input.zip"]
envVar          =  {}
license         =  True
command         =  "ls-dyna -n 2 -i neon.refined.rev01.k -p single"
cores           =  2
slots           =  1

#-----------------------------------------------------------------------------------------------------------------------
# This part is checking input parameters, no need to modify
core_code=rescale_system.get_core_code(core_name=core_name)

found_analysis=rescale_system.get_analysis(analysis_name=analysis_name)

analysis_code=found_analysis["code"]

rescale_system.check_analysis_version(found_analysis=found_analysis,version=version,core_code=core_code)

file_uploaded=rescale_system.direct_upload_file(file_name_list=file_name_list)


#-----------------------------------------------------------------------------------------------------------------------
# Create and submit jobs
job_id=rescale_system.create_job(job_name=job_name,license=license,command=command,analysis_code=analysis_code,
                                 versionCode=version,cores=cores,slots=slots,coretype=core_code,input_file=file_uploaded)
rescale_system.submit_job(job_ID=job_id)



#-----------------------------------------------------------------------------------------------------------------------
# Monitor job status and start the second job
complete=rescale_system.monitor_job_completion(job_ID=job_id)

if complete==True:
    job_id2 = rescale_system.create_job(job_name=job_name, license=license, command=command, analysis_code=analysis_code,
                                       versionCode=version, cores=cores, slots=slots, coretype=core_code,
                                       input_file=file_uploaded)
    rescale_system.submit_job(job_ID=job_id2)

