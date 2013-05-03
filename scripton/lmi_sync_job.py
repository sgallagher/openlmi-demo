'''
Created on May 3, 2013

@author: sgallagh
'''
import time

class LMISyncJob:
    '''
    Handle asynchronous CIM jobs in a synchronous manner.
    '''

    # Define value for running job
    JOB_RUNNING = 4096
    
    # Define error codes
    SUCCESS = 0
    ERR_UNSPECIFIED = 2

    # Define job state variables
    JOB_STATE_NEW = 2
    JOB_STATE_Starting = 3
    JOB_STATE_RUNNING = 4
    JOB_STATE_SUSPENDED = 5
    JOB_STATE_SHUTTINGDOWN = 6
    JOB_STATE_COMPLETED = 7
    JOB_STATE_TERMINATED = 8
    JOB_STATE_KILLED = 9
    JOB_STATE_EXCEPTION = 10
    JOB_STATE_SERVICE = 11
    JOB_STATE_QUERY_PENDING = 12

    def __init__(self, namespace, lmiresult):
        '''
        Create a new synchronous job
        '''
        self.namespace = namespace
        self.ret = lmiresult[0]
        self.outparams = lmiresult[1]
        self.err = lmiresult[2]

    def finished(self):
        '''Determine whether this job is still running'''
        if (self.job.JobState == LMISyncJob.JOB_STATE_COMPLETED
            or self.job.JobState == LMISyncJob.JOB_STATE_TERMINATED
            or self.job.JobState == LMISyncJob.JOB_STATE_KILLED
            or self.job.JobState == LMISyncJob.JOB_STATE_EXCEPTION):
            # Job has run to completion
            return 1

        #Job is still going
        return 0

    def process(self):
        '''
        Process the job in a synchronous loop and return
        when it is complete.
        '''
        if self.ret == LMISyncJob.SUCCESS:
            # This was not actually an async routine
            # Just return immediately
            return(LMISyncJob.SUCCESS,
                   self.outparams,
                   self.err)
        elif self.ret != LMISyncJob.JOB_RUNNING:
            # Job never started up correctly. Return the
            # original result code, error message and outparams  
            return (LMISyncJob.ERR_UNSPECIFIED,
                    None,
                    self.err)

        self.job = self.outparams['job'].to_instance()
        while(not self.finished()):
            self.job = self.namespace.LMI_StorageJob.first_instance(
                          Key="InstanceID",
                          Value=self.job.InstanceId)
            time.sleep(0.01) #sleep 10 ms between polls

        # Process the result
        if (self.job.JobState != LMISyncJob.JOB_STATE_COMPLETED):
            return (self.job.ERR_UNSPECIFIED,
                    self.job.JobOutParameters,
                    self.job.JobStatus)
        
        return (LMISyncJob.SUCCESS,
                self.job.JobOutParameters,
                self.job.JobStatus)