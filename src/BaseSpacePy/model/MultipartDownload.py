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
import multiprocessing
import shutil
import sys

class downloadTask(object):
    def __init__(self, api, BSfileId, fileName, localPath, piece, partSize, totalSize, attempt, tempDir):
        self.api = api
        self.BSfileId = BSfileId      # the baseSpace fileId
        self.fileName = fileName    # the name of the file to download
        self.piece  = piece         # piece number
        self.partSize = partSize    # the size in bytes of each piece (except last piece)
        self.totalSize  = totalSize # the total size of the file in bytes
        self.localPath = localPath  # the path in which to store the downloaded file        
        self.attempt= attempt       # the # of attempts we've made to download this piece          
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
        return self
        
    def __str__(self):        
        return 'File id %s, piece %s, piece size %s, total size %s' % (self.BSfileId, self.piece, self.partSize, self.totalSize)
    
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
            # check if we are out of jobs or have been halted                
            if next_task is None or self.task_queue.qsize()==0 or self.halt.is_set():
                # Poison pill means shutdown
                print '%s: Exiting' % proc_name
                self.task_queue.task_done()
                return
            # if we have been paused, sleep for a bit then check back
            elif self.pause.is_set():                   
#                print '%s: Paused' % proc_name 
                time.sleep(3)                                       
            # do some work
            else:                                       
#                print '%s: %s' % (proc_name, next_task)
                # give any download job 5 tries
                for i in xrange(1,5):    
                    answer = next_task()                    
                    if answer.state == True:
                        self.task_queue.task_done()                   
                        self.result_queue.put(answer)
                        break
                    else:
                        print "Download task " + str(next_task.piece) + " failed, retry attempt " + str(i) + " with error msg: " + answer.err_msg
                if not answer.state == True:
                    print "Five consecutive fails, halting download task"        
                    # halt all other processes and set non-zero exit code
                    self.halt.set()                 
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
        self.setup()
    
    def __str__(self):
        return "MPU -  Status: " + self.Status +  \
                ", Workers: " + str(self.getRunningWorkerCount()) + \
                ", Run Time: " + str(self.getRunningTime())[:5] + 's' + \
                ", Queue Size: " + str(self.tasks.qsize()) + \
                ", Percent Completed: " + str(self.getProgressRatio())[:6] + \
                ", Avg Transfer Rate: " + self.getTransRate() + \
                ", Data Transferred: " + readable_bytes(self.getTotalTransferred())
    
    def __repr__(self):
        return str(self)
    
#    def run(self):
#        while self.Status=='Paused' or self.__checkQueue__():
#            time.sleep(self.wait)
#        return
    
    def setup(self):
        '''
        Determine number of file pieces to download, create communication and tasks queues, add workers to task queue 
        '''
        # determine the number of chunks to download 
        bs_file = self.api.getFileById(self.fileId)
        self.fileName = bs_file.Name
        totalSize = bs_file.Size
        self.zeroQCount = 0
        self.fileCount = int(math.ceil(totalSize/self.partSize)) + 1
        
        if self.verbose: 
            print "Total file size " + str(totalSize) + " bytes"
            print "Using split size " + str(self.partSize) + " bytes"
            print "File count " + str(self.fileCount)
            print "CPUs " + str(self.cpuCount)
            print "startChunk " + str(self.startChunk)
        
        # Establish communication and task queues
        self.tasks = multiprocessing.JoinableQueue()
        self.completedPool = multiprocessing.Queue()        
        for i in xrange(self.startChunk,self.fileCount+1):         
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
        
#    def __cleanUp__(self):
#        self.stats[0] +=1
    
    def startDownload(self, testInterval=5):
        '''
        Start workers, handle paused and other states, wait until workers finish to clean up small file downloads
        '''
        if self.Status=='Terminated' or self.Status=='Completed':
            raise Exception('Cannot resume a ' + self.Status + ' multi-part download session.')
        
        if self.Status == 'Initialized':
            self.StartTime = time.time()
            for w in self.consumers:
                w.start()
        if self.Status == 'Paused':
            self.pauseEvent.clear()
        self.Status = 'Running'
        
        # wait until tasks queues are empty, then finalize download
        i=0
        while not self.hasFinished():
            if self.verbose and i: print str(i) + ': ' + str(self)
            time.sleep(testInterval)
            i+=1
        self.finalize()
        return 1
    
    def finalize(self):
        '''
        Check that all file pieces downloaded successfully, re-assemble file parts into single file
        '''
        if self.getRunningWorkerCount():
            raise Exception('Error - finalize called on  a transfer with running processes.')
        if self.Status=='Running':
            # check that all parts downloaded successfully (first sleep to make sure we're ready)
            time.sleep(1)            
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
    
    def hasFinished(self):
        '''
        If the task queue is empty, halt all workers
        Return the count of available workers
        '''
        if self.Status == 'Initialized': 
            return 0            
        # TODO temporary hack, check if the queue is empty        
        if self.tasks.qsize()==0:
            self.zeroQCount +=1
        if self.zeroQCount>15:
            self.haltWorkers()
        
        return not self.getRunningWorkerCount()>0
    
#    def pauseWorkers(self):
#        self.pauseEvent.set()
#        self.Status = 'Paused'
    
    def haltWorkers(self):
        for c in self.consumers: 
            c.terminate()
            
    #def terminateAll(self):
    #    '''
    #    Stop all workers, call cleanup method(s) (delete all local files?)
    #    '''
    #    #self.Status = 'Terminated'
        
    def getStatus(self):
        return self.Status
    
    def getFileResponse(self):
        return self.remoteFile
    
    def getRunningWorkerCount(self):
        return sum([c.is_alive() for c in self.consumers])
    
    def getTransRate(self):
        if not self.getRunningTime()>0: 
            return '0 b/s' 
        return readable_bytes((self.totalTask - self.tasks.qsize())*self.partSize/self.getRunningTime()) + '/s'
    
    def getRunningTime(self):
        if self.StartTime==-1: 
            return 0
        else: 
            return time.time() - self.StartTime
    
    def getTotalTransferred(self):
        '''
        Returns the total data amount transferred in bytes
        '''
        return float((self.totalTask - self.tasks.qsize())*self.partSize)
            
    def getProgressRatio(self):
        currentQ = float(self.tasks.qsize())
        res = float(self.totalTask - currentQ)/self.totalTask
        if res>1.0: 
            res=1.0
        return str(res)

def readable_bytes(size, precision=2):
    """
    Utility function to display number of bytes in a human-readable form; BaseSpace uses the Base 2 definition of bytes
    """
    suffixes=['B','KB','MB','GB','TB']
    suffixIndex = 0
    while size > 1024:
        suffixIndex += 1 # increment the index of the suffix
        size = size / 1024.0 # apply the division
    return "%.*f %s"%(precision, size, suffixes[suffixIndex])
    