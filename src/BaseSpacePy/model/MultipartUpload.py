"""
Copyright 2012 Illumina

    Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://www.apache.org/licenses/LICENSE-2.0
 
    Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import time
import os
import math
from hashlib import md5
import pycurl
from subprocess import *
#from multiprocessing import Process, Value, Queue, Lock
import json
import multiprocessing
import base64

class uploadTask(object):
    def __init__(self, api, BSfileId, piece, total, myfile, attempt):
        self.api    = api
        self.piece  = piece   # piece number 
        self.total  = total   # out of total piece count
        self.file   = myfile  # the local file to be uploaded
        self.BSfileId=BSfileId# the baseSpace fileId
        self.attempt= attempt # the # of attempts we've made to upload this guy  
        self.state  = 0       # 0=pending, 1=ran, 2=error 
    
    def uploadFileName(self):
        return self.file.split('/')[-1] + '_' + str(self.piece)
    
    def __call__(self):
        # read the byte string in
        self.attempt += 1
        transFile = self.file + str(self.piece)
        cmd = "split -d -n " + str(self.piece) + '/' + str(self.total) + ' ' + self.file
        process = os.popen(cmd)
        out = process.read()
        process.close()
        f = open(transFile,'w')
        f.write(out)
        f.close()
        self.md5 = md5(out).digest().encode('base64')

        res = self.api.__uploadMultipartUnit__(self.BSfileId,self.piece,self.md5,transFile)
        os.system('rm ' + transFile)
#        print "my result " + str(res)
        if res['Response'].has_key('ETag'): self.state = 1          # case things went well
        else: self.state = 2
        return self
        
    def __str__(self):
        return '%s / %s - %s' % (self.piece, self.total, self.file)
    
class Consumer(multiprocessing.Process):
    
    def __init__(self, task_queue, result_queue,pauseEvent,haltEvent):
        multiprocessing.Process.__init__(self)
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.pause = pauseEvent
        self.halt  = haltEvent
    
    def run(self):
        proc_name = self.name
        while True:
            if not self.pause.is_set(): next_task = self.task_queue.get()
            
            if next_task is None or self.halt.is_set(): # check if we are out of jobs or have been halted
                # Poison pill means shutdown
#                print '%s: Exiting' % proc_name
                self.task_queue.task_done()
                break
            elif self.pause.is_set():                   # if we have been paused, sleep for a bit then check back
#                print '%s: Paused' % proc_name 
                time.sleep(3)                                       
            else:                                       # do some work
#                print '%s: %s' % (proc_name, next_task)
                answer = next_task()
                self.task_queue.task_done()
                if answer.state == 1:                   # case everything went well
                    self.result_queue.put(answer)
                else:                                   # case something sent wrong
                    if next_task.attempt<3:
                        self.task_queue.put(next_task)  # queue the guy for a retry
                    else:                               # problems, shutting down this party
                        self.halt.set()                 # halt all other process
        return

class MultipartUpload:
    def __init__(self,api,aId,localFile,fileObject,cpuCount,partSize,tempdir,startChunk=1,verbose=0):
        self.api            = api
        self.analysisId     = aId
        self.localFile      = localFile     # File object
        self.remoteFile     = fileObject
        self.partSize       = partSize
        self.cpuCount       = cpuCount
        self.verbose        = verbose
        self.tempDir        = tempdir       #
        self.Status         = 'Initialized'
        self.StartTime      = -1
        self.startChunk     = startChunk
#        self.repeatCount    = 0             # number of chunks we uploaded multiple times
        self.setup()
    
    def __str__(self):
        return "MPU -  Stat: " + self.Status +  ", LiveThread: " + str(self.getRunningThreadCount()) + \
                ", RunTime: " + str(self.getRunningTime())[:5] + 's' + \
                ", Q-size " + str(self.tasks.qsize()) + \
                ", Completed " + str(self.getProgressRatio()) + \
                ", AVG TransferRate " + self.getTransRate() + \
                ", Data transfered " + str(self.getTotalTransfered())[:5] + 'Gb'
    
    def __repr__(self):
        return str(self)
    
    def run(self):
        while self.Status=='Paused' or self.__checkQueue__():
            time.sleep(self.wait)
        return
    
    def setup(self):
        
        # determine the 
#        print self.localFile
        totalSize = os.path.getsize(self.localFile)
        fileCount = int(math.ceil(totalSize/(self.partSize*1024.0*1000)))
        
        if self.verbose: 
            print "TotalSize " + str(totalSize)
            print "Using split size " + str(self.partSize) +"Mb"
            print "Filecount " + str(fileCount)
            print "CPUs " + str(self.cpuCount)
            print "startChunk " + str(self.startChunk)
        
        # Establish communication queues
        self.tasks = multiprocessing.JoinableQueue()
        self.completedPool = multiprocessing.Queue()
        for i in xrange(self.startChunk,fileCount+1):         # set up the task queue
            t = uploadTask(self.api,self.remoteFile.Id,i, fileCount, self.localFile, 0)
            self.tasks.put(t)
        self.totalTask  = self.tasks.qsize()
        
        # create consumers
        self.pauseEvent = multiprocessing.Event()
        self.haltEvent = multiprocessing.Event()
        if self.verbose:
            print 'Creating %d consumers' % self.cpuCount
            print "queue size " + str(self.tasks.qsize())
        self.consumers = [ Consumer(self.tasks, self.completedPool,self.pauseEvent,self.haltEvent) for i in xrange(self.cpuCount) ]
        for c in self.consumers: self.tasks.put(None)   # add poisson pill
        
    def __cleanUp__(self):
        self.stats[0] +=1
    
    def startUpload(self,returnOnFinish=0,testInterval=5):
        if self.Status=='Terminated' or self.Status=='Completed':
            raise Exception('Cannot resume a ' + self.Status + ' multi-part upload session.')
        
        if self.Status == 'Initialized':
            self.StartTime = time.time()
            for w in self.consumers:
                w.start()
        if self.Status == 'Paused':
            self.pauseEvent.clear()
        self.Status = 'Running'
        
        # If returnOnFinish is set 
        if returnOnFinish:
            i=0
            while not self.hasFinished():
                if self.verbose and i: print str(i) + ': ' + str(self)
                time.sleep(testInterval)
                i+=1
            self.finalize()
            return 1
        else:
            self.finalize()
            return 1
    
    def finalize(self):
        if self.getRunningThreadCount():
            raise Exception('Cannot finalize a transfer with running threads.')
        if self.Status=='Running':
            time.sleep(1)               # sleep one to make sure 
            print self.remoteFile.Id
            self.remoteFile = self.api.markFileState(self.remoteFile.Id)
            self.Status=='Completed'
        else:
            raise Exception('To finalize the status of the transfer must be "Running."')
#    
    def hasFinished(self):
        if self.Status == 'Initialized': return 0
        return not self.getRunningThreadCount()>0
    
    def pauseUpload(self):
        self.pauseEvent.set()
        self.Status = 'Paused'
#    
    def haltUpload(self):
        for c in self.consumers: c.terminate()
        self.Status = 'Terminated'
    
    def getStatus(self):
        return self.Status
    
    def getFileResponse(self):
        return self.remoteFile
    
    def getRunningThreadCount(self):
        return sum([c.is_alive() for c in self.consumers])
    
    def getTransRate(self):
                # tasks completed                        size of file-parts
        if not self.getRunningTime()>0: return '0 mb/s' 
        return str((self.totalTask - self.tasks.qsize())*self.partSize/self.getRunningTime())[:6] + ' mb/s'
    
    def getRunningTime(self):
        if self.StartTime==-1: return 0
        else: return time.time() - self.StartTime
    
    def getTotalTransfered(self):
        '''
        Returns the total data amount transfered in Gb
        '''
        return float((self.totalTask - self.tasks.qsize())*self.partSize)/1000.0
        
    
    def getProgressRatio(self):
        currentQ = float(self.tasks.qsize())
        res = float(self.totalTask - currentQ)/self.totalTask
        if res>1.0: res=1.0
        return str(res)[:5]