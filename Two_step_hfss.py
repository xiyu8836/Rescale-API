#!/usr/bin/python

import requests
import json
import time

api_token='Token bd2128efa577985cd87a4c338415ef3c059e1559'
file_name='Diff_Via_tight_conv.aedtz'
if file_name[-1] == "z":
    file_name2=file_name[:-1]
else:
    file_name=file_name

# upload input files: how to upload multiple files at one time?
file_upload=requests.post(
    'https://platform.rescale.com/api/v2/files/contents/',
    data=None,
    files={'file': open('submit_frequency_sweep.sh')},
    headers={'Authorization': api_token}
)
file_upload1=requests.post(
    'https://platform.rescale.com/api/v2/files/contents/',
    data=None,
    files={'file': open('credentials')},
    headers={'Authorization': api_token}
)
file_upload2=requests.post(
    'https://platform.rescale.com/api/v2/files/contents/',
    data=None,
    files={'file': open('rescale.jar')},
    headers={'Authorization': api_token}
)
file_upload3=requests.post(
    'https://platform.rescale.com/api/v2/files/contents/',
    data=None,
    files={'file': open(file_name)},
    headers={'Authorization': api_token}
)
file_upload4=requests.post(
    'https://platform.rescale.com/api/v2/files/contents/',
    data=None,
    files={'file': open('submit_frequency_sweep_2nd.sh')},
    headers={'Authorization': api_token}
)
file_content=json.loads(file_upload.text)
file_content1=json.loads(file_upload1.text)
file_content2=json.loads(file_upload2.text)
file_content3=json.loads(file_upload3.text)
file_content4=json.loads(file_upload4.text)

# obtain file ID after uploading for later use-create jobs
file_ID=file_content["id"]
file_ID1=file_content1["id"]
file_ID2=file_content2["id"]
file_ID3=file_content3["id"]
file_ID4=file_content4["id"]
'''
analysis=requests.get(
    'https://platform.rescale.com/api/v2/anaylyses/',
    headers={'Authorization': api_token}
)

# core information
core_types=requests.get(
    'https://platform.rescale.com/api/v2/coretypes/',
    headers={'Authorization': api_token}
)
content=json.loads(core_types.text)
print content["results"][0]["code"]
'''
# job created but not submitted
job_setup=requests.post(
    'https://platform.rescale.com/api/v2/jobs/',
    json={
        "name":"HFSS 2STEP Auto 1st step %s" % file_name,
        "jobanalyses": [
            {
                "useRescaleLicense": True,
                "command": "cp /program/ansys_182/18.2/AnsysEM18.2/Linux64/Examples/HFSS/RF\ Microwave/OptimTee.aedt .\n\
export TASKS_PER_NODE=-1\n\
for host in `cat $HOME/machinefile` ; do echo ${host}:${TASKS_PER_NODE}:${RESCALE_CORES_PER_NODE}:90%% >> $HOME/work/machinefile.hfss; done\n\
ansysedt -auto -distributed -monitor -machinelist file=$HOME/work/machinefile.hfss -ng -batchoptions \"\'HFSS/SolveAdaptiveOnly\'=1\" -batchsolve %s\n\
./submit_frequency_sweep.sh --credentials-file credentials --input %s --core-type Zinc --num-cores 8 --on-demand --analysis HFSS" % (file_name,file_name2),
                "analysis": {
                    "code":"ansys_hfss",
                    "version":"19.2"
                },
                "hardware":{
                    "coresPerSlot":8,
                    "slots":1,
                    "coreType":"hpc-plus"
                },
                "inputFiles":[
                    {
                        # How to reference multiple files??
                        "id":file_ID,
                     },
                    {
                        # How to reference multiple files??
                        "id": file_ID1,
                    },
                    {
                        # How to reference multiple files??
                        "id": file_ID2,
                    },
                    {
                        # How to reference multiple files??
                        "id": file_ID3,
                    },
                    {
                        # How to reference multiple files??
                        "id": file_ID4,
                    }
                ]
            }
        ]
    },
    headers={'Authorization': api_token}
)

# print job_setup.content
job_content=json.loads(job_setup.text)
job_ID=job_content["id"]
print job_ID

#submit the job
requests.post(
    'https://platform.rescale.com/api/v2/jobs/%s/submit/'%job_ID,
    headers={'Authorization': api_token}
)

# wait for the job to start
'''
start = int(time.time())
print ('start:%d' % start)
# n = 0
# the first 15 seconds

time.sleep(15)
end = int(time.time())
print ('end:%d' % end)
status=True
'''
'''
# check status every 15 seconds
while status:
    print ('start:%d' % start)
    print ('end:%d' % end)

    # if (end - start) % 15 == 0:
        #print('it is 15 seconds later')
        #n = n + 1
        # check the status of the previous job
    pre_job=requests.get(
        'https://platform.rescale.com/api/v2/jobs/%s/statuses/' % job_ID,
        headers={'Authorization': api_token}
    )
    pre_job_response = json.loads(pre_job.text)

    # if previous job completed, the second job will be triggered
    if pre_job_response["count"]==7 and pre_job_response["results"][0]["status"]=="Completed":
        print ('it is there')
        # submit the second job

        job_setup2 = requests.post(
            'https://platform.rescale.com/api/v2/jobs/',
                json={
                    "name": "HFSS 2STEP Auto Python API Setup-2nd step",
                    "jobanalyses": [
                        {
                            "useRescaleLicense": True,
                            "command": "./submit_frequency_sweep.sh --credentials-file credentials --input pyramidal_horn_with_interpolating_sweep.aedt --core-type Zinc --num-cores 8 --on-demand --analysis HFSS",
                            "analysis": {
                                "code": "ansys_hfss",
                                "version": "19.2"
                            },
                            "hardware": {
                                "coresPerSlot": 8,
                                "slots": 1,
                                "coreType": "hpc-plus"
                            },
                            "inputFiles": [
                                {
                                    # How to reference multiple files??
                                    "id": file_ID,
                                },
                                {
                                    # How to reference multiple files??
                                    "id": file_ID1,
                                },
                                {
                                    # How to reference multiple files??
                                    "id": file_ID2,
                                },
                                {
                                    # How to reference multiple files??
                                    "id": file_ID3,
                                }
                            ]
                        }
                    ]
                },
                headers={'Authorization': api_token}
            )

            # print job_setup.content
        job_content2 = json.loads(job_setup2.text)
        job_ID2 = job_content2["id"]
        print job_ID2
        requests.post(
                'https://platform.rescale.com/api/v2/jobs/%s/submit/' % job_ID2,
                headers={'Authorization': api_token}
            )
        status = False
    else:
        print ("not there yet")
        time.sleep(15)

    end=int(time.time())

'''
"""cp /program/ansys_182/18.2/AnsysEM18.2/Linux64/Examples/HFSS/RF\ Microwave/OptimTee.aedt .
export TASKS_PER_NODE=-1
for host in `cat $HOME/machinefile` ; do echo ${host}:${TASKS_PER_NODE}:${RESCALE_CORES_PER_NODE}:90% >> $HOME/work/machinefile.hfss; done
ansysedt -auto -distributed -monitor -machinelist file=$HOME/work/machinefile.hfss -ng -batchoptions "'HFSS/SolveAdaptiveOnly'=1" -batchsolve pyramidal_horn_with_interpolating_sweep.aedt
./submit_frequency_sweep.sh --credentials-file credentials --input pyramidal_horn_with_interpolating_sweep.aedt --core-type Zinc --num-cores 8 --on-demand --analysis HFSS"""
'''
'''
