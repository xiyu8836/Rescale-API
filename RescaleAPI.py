#!/usr/bin/python

import requests
import json
import time
import sys
import os

class RescaleAPI(object):
    def __init__(self,api_key,api_url):
        self.api_key=api_key
        self.api_url=api_url
        self.core_types={}
        self.analyses={}
        self.inputfiles_uploaded={}
        self.jobs={}

    def all_core_info(self):
        self.core_types={}
        url="%s/api/v2/coretypes/" % self.api_url

        while url:
            response = requests.get(
                url,
                headers={'Authorization': 'Token %s' % self.api_key}
            )
            content = json.loads(response.text)

            for core_info in content["results"]:
                self.core_types[core_info["name"]]=core_info["code"]

            url=content["next"]

        #return self.core_types

    def get_core_code(self,core_name=''):
        exist=False
        self.all_core_info()

        for core_name_list in self.core_types:
            if core_name_list == core_name:
                exist=True
                return self.core_types[core_name_list]

        if exist == False:
            print("There is no core type: %s, please verify"%core_name)
            print("Available core names are:")
            for core_name in self.core_types:
                print(core_name)

            sys.exit()

    # get information for all analyses
    def all_analysis_info(self):
        self.analyses={}
        url="%s/api/v2/analyses/" % self.api_url

        while url:
            response = requests.get(
                url,
                headers={'Authorization': 'Token %s' % self.api_key}
            )
            content = json.loads(response.text)

            for analysis_info in content["results"]:
                self.analyses[analysis_info["name"]]=analysis_info

            url=content["next"]

        #return self.analyses

    # search the analysis information based on analysis name
    # determine if the analysis name is correct based on user input
    # return analysis code and version info
    def get_analysis(self,analysis_name=''):
        exist=False
        self.all_analysis_info()
        found_analysis={}

        for analysis_name_list in self.analyses:
            if analysis_name_list == analysis_name:
                exist=True
                found_analysis["code"]=self.analyses[analysis_name]["code"]
                found_analysis["versions"]=self.analyses[analysis_name]["versions"]
                return found_analysis

        if exist == False:
            print("There is no analysis software: %s, please verify"%analysis_name)
            print("Available analyses are:")
            for analysis_name in self.analyses:
                print(analysis_name)

            sys.exit()


    # after found_analysis is returned, information of "code" and "versions" are
    # stored, this function test if version is correct and if core types match with given info
    # version used should be version code of the analysis instead of version
    def check_analysis_version(self,found_analysis={},version='',core_code=''):
        exist1=False
        exist2=False

        for version_list in found_analysis["versions"]:
            if version_list["versionCode"]==version:
                exist1=True
                core_type_allowed_here=version_list["allowedCoreTypes"]

            for core_type_allowed in version_list["allowedCoreTypes"]:
                if core_code==core_type_allowed:
                    exist2=True

        if exist1==True and exist2 == True:
            print("Analysis version and core type matched! Proceed...")
            return
        elif exist1 == False:
            print("Check analysis version code, no such version code: %s"%version)
            print("All versions available are here:")
            for version_list_content in found_analysis["versions"]:
                print(version_list_content["versionCode"])

            sys.exit()
        elif exist2 == False:
            print("Check core type: %s, such core type cannot be used in this analysis version"%core_code)
            print("Available core types for this version are:")
            for core_allowed_here in core_type_allowed_here:
                print(core_allowed_here)

            sys.exit()
        else:
            print("Both analysis version and core type are wrong!")
            sys.exit()

    # upload a file without checking if the file is in the system
    # return a dictionary: {file_name:file_id}
    def direct_upload_file(self,file_name_list=[]):
        file_uploaded={}
        for file_name in file_name_list:
            response = requests.post(
                '%s/api/v2/files/contents/'%self.api_url,
                #data=None,
                files={'file': open(file_name)},
                headers={'Authorization': 'Token %s' % self.api_key}
            )
            content = json.loads(response.text)

            file_uploaded[content["name"]]=content["id"]

        return file_uploaded

    # first check if there is a file in "uploaded input files" matching the file list,
    # only upload those are not already in the files on platform
    # return a dictionary containing all files to be used (including already uploaded and to be uploaded): {file_name:file_id}
    def upload_file_diffname(self,file_name_list=[]):
        self.inputfiles_uploaded = {}
        # directly got own files, uploaded, and for input
        url = "%s/api/v2/files/?type=1&isUploaded=true&owner=1" % self.api_url
        file_to_use={}

        while url:
            print(url)
            response = requests.get(
                url,
                headers={'Authorization': 'Token %s' % self.api_key}
            )
            content = json.loads(response.text)


            for file_info in content["results"]:
                self.inputfiles_uploaded[file_info["name"]]=file_info["id"]

            url = content["next"]


        for file_to_upload in file_name_list:
            find_file=False
            for file_already_uploaded in self.inputfiles_uploaded:
                if file_already_uploaded == file_to_upload:
                    print("file %s is already on the platform, will not be uploaded, but will be accessed" % file_to_upload)
                    file_to_use[file_to_upload]=self.inputfiles_uploaded[file_already_uploaded]
                    find_file=True
                    break

            if find_file == False:
                print("file %s is not on the platform, will be uploaded and accessed" % file_to_upload)
                response = requests.post(
                    '%s/api/v2/files/contents/' % self.api_url,
                    # data=None,
                    files={'file': open(file_to_upload)},
                    headers={'Authorization': 'Token %s' % self.api_key}
                )
                content = json.loads(response.text)

                file_to_use[content["name"]] = content["id"]

        return file_to_use

    # create a job by referring to input parameters
    def create_job(self,job_name='',license=True,command='',analysis_code='',versionCode='',
                   cores=0,slots=0,coretype='',input_file=[],envVAR={}):
        #job_num = len(job_name)
        input_file_id=[]
        for file_name in input_file:
            file_info={"id":input_file[file_name]}
            input_file_id.append(file_info)

        job_data = {
                   "name": job_name,
                   "jobanalyses": [
                       {
                           "envVars":envVAR,
                           "useRescaleLicense": license,
                           "command": command,
                           "analysis": {
                               "code": analysis_code,
                               "version": versionCode
                           },
                           "hardware": {
                               "coresPerSlot": cores,
                               "slots": slots,
                               "coreType": coretype
                           },
                           "inputFiles": input_file_id
                       }
                   ]
               }

        #print job_data

        response = requests.post(
            '%s/api/v2/jobs/' % self.api_url,
            json=job_data,
            headers={'Authorization': 'Token %s' % self.api_key,
                     'Content-Type': 'application/json'}
        )

        # print job_setup.content
        content = json.loads(response.text)
        job_ID = content["id"]
        print("Job '%s' has been created with id %s" %(job_name,job_ID))

        return job_ID

    def submit_job(self,job_ID=''):
        requests.post(
            'https://platform.rescale.com/api/v2/jobs/%s/submit/' % job_ID,
            headers={'Authorization': 'Token %s' % self.api_key}
        )
        print("Job %s has been submitted" % (job_ID))

# monitor if the job is completed, need manually stop if job running has problems and cannot stop by itself
# this function assumes the job run
    def monitor_job_completion(self,job_ID=''):
        complete=False
        status=True
        time.sleep(5)
        while status:
            response = requests.get(
                '%s/api/v2/jobs/%s/statuses/' % (self.api_url,job_ID),
                headers={'Authorization': 'Token %s' % self.api_key}
            )
            content = json.loads(response.text)

            if content["results"][0]["status"] == "Completed":
                print("Job %s is completed."%job_ID)
                complete=True
                return complete
            else:
                time.sleep(15)

    def get_job_file_id(self,file_name,job_ID):
        response = requests.get(
            '%s/api/v2/jobs/%s/files/?search=%s' % (self.api_url,job_ID,file_name),
            headers={'Authorization': 'Token %s' % self.api_key}
        )
        content = json.loads(response.text)
        file_id = content['results'][0]['id']
        return file_id

    def download_job_file(self,file_id):
        response = requests.get(
            '%s/api/v2/files/%s/contents/' % (self.api_url, file_id),
            headers={'Authorization': 'Token %s' % self.api_key}
        )

        with open('file_downloaded', 'wb') as fd:
            for chunk in response.iter_content(chunk_size=2048):
                fd.write(chunk)

    def upload_file_CLI(self,file_name_list=[]):
        all_file=""
        file_id_list=[]
        for file_name in file_name_list:
            file_name=file_name+" "
            all_file=all_file+file_name

        upload_command="java -jar /usr/local/bin/rescale.jar upload -f %s" % all_file
        os.system(upload_command)

        for file_name in file_name_list:
            content=self.search_file_with_name(file_name)
            file_id_list.append(content['results'][0]['id'])

        return file_id_list

    def search_file_with_name(self,file_name):
        response = requests.get(
            '%s/api/v2/files/?search=%s' % (self.api_url, file_name),
            headers={'Authorization': 'Token %s' % self.api_key}
        )
        content = json.loads(response.text)
        return content
    
    def new_func(self,new)
        print(new)
   



