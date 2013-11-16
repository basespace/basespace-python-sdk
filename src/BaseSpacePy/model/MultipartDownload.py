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
import json
import multiprocessing
import base64
import shutil
import sys

class downloadTask(object):
    def __init__(self, api, BSfileId, fileName, localPath, piece, partSize, totalSize, attempt, tempDir):
        self.api    = api
        self.BSfileId=BSfileId      # the baseSpace fileId
        self.fileName = fileName    # the name of the file to download
        self.piece  = piece         # piece number
        self.partSize = partSize    # the size in MB of each piece (except last piece)
        self.totalSize  = totalSize # the total size of the file in bytes
        self.localPath = localPath  # the path in which to store the downloaded file        
        self.attempt= attempt       # the # of attempts we've made to upload this guy          
        self.tempDir = tempDir
        self.partSize = partSize
        
        self.state  = 0             # 0=pending, 1=ran, 2=error 
    
    #def downloadFileName(self):
    #    return self.file.split('/')[-1] + '_' + str(self.piece)
    
    def __call__(self):
        '''
        Download a chunk of the target file
        '''
        self.attempt += 1
        transFile = os.path.join(self.tempDir, self.fileName + "." + str(self.piece))
        # calculate byte range
        startbyte = (self.piece - 1) * self.partSize
        endbyte = (self.piece * self.partSize) - 1
        if endbyte > self.totalSize:
            endbyte = self.totalSize - 1
        try:
            self.api.fileDownload(self.BSfileId, self.localPath, transFile, [startbyte, endbyte])
        except Exception as e:
            self.state = False
            self.err_msg = str(e)
        else:
            self.state = True
            #self.err_msg = "testing"
        # TODO, is md5 check occurring? (is it set by AWS?)                                                
        return self
        
    def __str__(self):
        # TODO substitute file id for file name
        return '%s / %s - %s' % (self.piece, self.totalSize, self.BSfileId)
    
class Consumer(multiprocessing.Process):
    
    def __init__(self, task_queue, result_queue, pauseEvent, haltEvent):
        multiprocessing.Process.__init__(self)
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.pause = pauseEvent
        self.halt  = haltEvent
        self.timeOutTask = 60   # seconds for a task to timeout
        
    def run(self):
        proc_name = self.name
        while True:
            if not self.pause.is_set(): 
                next_task = self.task_queue.get()            
            if next_task is None or self.task_queue.qsize()==0 or self.halt.is_set(): # check if we are out of jobs or have been halted
                # Poison pill means shutdown
                print '%s: Exiting' % proc_name
                self.task_queue.task_done()
                return
            elif self.pause.is_set():                   # if we have been paused, sleep for a bit then check back
#                print '%s: Paused' % proc_name 
                time.sleep(3)                                       
            else:                                       # do some work
#                print '%s: %s' % (proc_name, next_task)
                # give any download job 5 tries
                for i in xrange(0,5):    
                    answer = next_task()
                    if answer.state == True:
                        self.task_queue.task_done()                   # case everything went well
                        self.result_queue.put(answer)
                        break
                    else:
                        print "Download task " + str(next_task.piece) + " failed, retry attempt " + str(i) + " with error msg: " + answer.err_msg
                if not answer.state == True:
                    print "Five consecutive fails, halting download task"        
                    self.halt.set()                 # halt all other process
                    sys.exit(1)
        return

class MultipartDownload:
    def __init__(self, api, fileId, localPath, cpuCount, partSize, tempDir, startChunk=1, verbose=0):
        self.api            = api
        self.fileId         = fileId
        self.localPath      = localPath        
        self.partSize       = partSize
        self.cpuCount       = cpuCount
        self.verbose        = verbose
        self.tempDir        = tempDir
        self.Status         = 'Initialized'
        self.StartTime      = -1
        self.startChunk     = startChunk
        self.zeroQCount     = 0  
#        self.repeatCount    = 0             # number of chunks we downloaded multiple times
        self.setup()
    
    def __str__(self):
        return "MPU -  Stat: " + self.Status +  ", LiveThread: " + str(self.getRunningThreadCount()) + \
                ", RunTime: " + str(self.getRunningTime())[:5] + 's' + \
                ", Q-size " + str(self.tasks.qsize()) + \
                ", Completed " + str(self.getProgressRatio()) + \
                ", AVG TransferRate " + self.getTransRate() + \
                ", Data transferred " + str(self.getTotalTransfered())[:5] + 'Gb'
    
    def __repr__(self):
        return str(self)
    
    def run(self):
        while self.Status=='Paused' or self.__checkQueue__():
            time.sleep(self.wait)
        return
    
    def setup(self):
        
        # determine the number of chunks to download 
        bs_file = self.api.getFileById(self.fileId)
        self.fileName = bs_file.Name
        totalSize = bs_file.Size
        self.zeroQCount = 0
        #totalSize = os.path.getsize(self.localFile)
        self.fileCount = int(math.ceil(totalSize/self.partSize)) + 1
        
        if self.verbose: 
            print "TotalSize " + str(totalSize)
            print "Using split size " + str(self.partSize) +" bytes"
            print "Filecount " + str(self.fileCount)
            print "CPUs " + str(self.cpuCount)
            print "startChunk " + str(self.startChunk)
        
        # Establish communication queues
        self.tasks = multiprocessing.JoinableQueue()
        self.completedPool = multiprocessing.Queue()
        for i in xrange(self.startChunk,self.fileCount+1):         # set up the task queue
            t = downloadTask(self.api, self.fileId, self.fileName, self.localPath, i, self.partSize, totalSize, 0, self.tempDir)
            self.tasks.put(t)
        self.totalTask  = self.tasks.qsize()
        
        # create consumers
        self.pauseEvent = multiprocessing.Event()
        self.haltEvent = multiprocessing.Event()
        if self.verbose:
            print 'Creating %d consumers' % self.cpuCount
            print "queue size " + str(self.tasks.qsize())
        self.consumers = [ Consumer(self.tasks, self.completedPool,self.pauseEvent,self.haltEvent) for i in xrange(self.cpuCount) ]
        for c in self.consumers:
            self.tasks.put(None)   # add poison pill
        
    def __cleanUp__(self):
        self.stats[0] +=1
    
    def startDownload(self,returnOnFinish=0,testInterval=5):
        if self.Status=='Terminated' or self.Status=='Completed':
            raise Exception('Cannot resume a ' + self.Status + ' multi-part download session.')
        
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
            print 'Finalize called on  a transfer with running threads, halting all remaining threads.'
            self.haltUpload()
        if self.Status=='Running':
            time.sleep(1)               # sleep one to make sure
            # check that all parts downloaded successfully
            reassemble = True
            for w in self.consumers:
                if w.exitcode is None:
                    raise Exception('Error - at least one process is active when all processes should be terminated')
                if w.exitcode != 0:
                    reassemble = False
            if reassemble:              
                if self.verbose:
                    print "Assembling downloaded file parts into single file"                                           
                # re-assemble downloaded parts into single file 
                part_files = [os.path.join(self.tempDir, self.fileName + '.' + str(i)) for i in xrange(self.startChunk,self.fileCount+1)]            
                with open(os.path.join(self.localPath, self.fileName), 'w+b') as whole_file:
                    for part_file in part_files:
                        shutil.copyfileobj(open(part_file, 'r+b'), whole_file)                 
                # delete temp part files
                for part_file in part_files:
                    os.remove(part_file)                
            # TODO option to delete downloaded piece files? Could resume with these...?
            self.Status = 'Completed'
        else:
            raise Exception('To finalize, the status of the transfer must be "Running."')
#    
    def hasFinished(self):
        if self.Status == 'Initialized': 
            return 0            
        # TODO temporary hack, check if the queue is empty        
        if self.tasks.qsize()==0:
            self.zeroQCount +=1
        if self.zeroQCount>15:
            self.haltDownload()
        
        return not self.getRunningThreadCount()>0
    
    def pauseDownload(self):
        self.pauseEvent.set()
        self.Status = 'Paused'
#    
    def haltDownload(self):
        for c in self.consumers: c.terminate()
#        self.Status = 'Terminated'
    
    def getStatus(self):
        return self.Status
    
    def getFileResponse(self):
        return self.remoteFile
    
    def getRunningThreadCount(self):
        return sum([c.is_alive() for c in self.consumers])
    
    def getTransRate(self):
                # tasks completed                        size of file-parts
        if not self.getRunningTime()>0: return '0 mb/s' 
        return str((self.totalTask - self.tasks.qsize())*self.partSize/self.getRunningTime())[:6] + ' b/s'
    
    def getRunningTime(self):
        if self.StartTime==-1: return 0
        else: return time.time() - self.StartTime
    
    def getTotalTransfered(self):
        '''
        Returns the total data amount transfered in bytes
        '''
        return float((self.totalTask - self.tasks.qsize())*self.partSize)
        
    
    def getProgressRatio(self):
        currentQ = float(self.tasks.qsize())
        res = float(self.totalTask - currentQ)/self.totalTask
        if res>1.0: res=1.0
        return str(res)[:5]