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
import Queue
import shutil
import sys

class DownloadTask(object):
    def __init__(self, api, bs_file_id, file_name, local_path, piece, part_size, total_size, attempt, temp_dir):
        self.api = api                # BaseSpace api object
        self.bs_file_id = bs_file_id  # the baseSpace fileId
        self.file_name = file_name    # the name of the file to download
        self.piece  = piece           # piece number
        self.part_size = part_size    # the size in bytes of each piece (except last piece)
        self.total_size  = total_size # the total size of the file in bytes
        self.local_path = local_path  # the path in which to store the downloaded file        
        self.attempt= attempt         # the # of attempts we've made to download this piece          
        self.temp_dir = temp_dir
        
        # tasks must implement these attributes
        self.success  = False
        self.err_msg = "no error"         
    
    def __call__(self):
        '''
        Download a chunk of the target file
        '''
        # TODO surround with try except to avoid unpicklable exception that may block?
        self.attempt += 1
        transFile = os.path.join(self.temp_dir, self.file_name + "." + str(self.piece))
        # calculate byte range
        startbyte = (self.piece - 1) * self.part_size
        endbyte = (self.piece * self.part_size) - 1
        if endbyte > self.total_size:
            endbyte = self.total_size - 1
        try:
            self.api.fileDownload(self.bs_file_id, self.local_path, transFile, [startbyte, endbyte])
        except Exception as e:
            self.success = False
            self.err_msg = str(e)
            # TODO clean up partially downloaded file?
        else:
            # TODO test that downloaded file is correct size
            if os.path.getsize(os.path.join(self.local_path, transFile)) != endbyte - startbyte + 1:
                self.success = False
                self.err_msg = "ERROR - downloaded file chunk has incorrect size, for task: " + str(self)
            else:
                self.success = True
        return self
        
    def __str__(self):        
        #return 'File id %s, piece %s, piece size %s, total size %s' % (self.bs_file_id, self.piece, self.part_size, self.total_size)
        return 'File piece %s, piece size %s' % (self.piece, self.part_size)
    
class Consumer(multiprocessing.Process):
    
    def __init__(self, task_queue, result_queue, pauseEvent, haltEvent):
        multiprocessing.Process.__init__(self)
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.pause = pauseEvent
        self.halt  = haltEvent
       # self.timeOutTask = 60   # seconds for a task to timeout
        
        self.retries = 1
        
    def run(self):
        '''
        Executes tasks from the task queue until poison pill is reached or halt signal found; has pause capability
        '''
        while True:
            # get next task unless paused
            if not self.pause.is_set(): 
                next_task = self.task_queue.get()
            print "    processing task: " + str(next_task)
            # poison pill means we're at the end of the task queue                
            if next_task is None:            
                print 'Worker halting, found final task for worker %s' % self.name
                #self.task_queue.task_done()
                break                
            # task queue empty -- shouldn't need this due to poison pill -- may block if queue somehow gets empty?
            elif self.task_queue.qsize()==0:
                print 'Worker halting, found task queue empty for worker %s' % self.name
                #self.task_queue.task_done()
                break
            elif self.halt.is_set():
                print 'Worker halting, found halt signal for worker %s' % self.name
                #self.task_queue.task_done() # TODO hmmm, didn't process task but marked it as done...?
                break #sys.exit()                                            
            elif self.pause.is_set():                   
                time.sleep(3)                                       
            else:                                                       
                # attempt to run tasks, with retry
                for i in xrange(1, self.retries + 1):    
                    answer = next_task()                    
                    if answer.success == True:
                        #self.task_queue.task_done()                   
                        self.result_queue.put(answer)
                        break
                    else:
                        print "Worker retrying task " + str(next_task) + " after failure, retry attempt " + str(i) + " with error msg: " + answer.err_msg
                if not answer.success == True:
                    print "Worker halting, too many failures with retry for worker %s" % str(self)        
                    # add failed answer to result queue and set halt event for all workers
                    #self.task_queue.task_done()                   
                    self.result_queue.put(answer)                    
                    self.halt.set()
                    break
                    #sys.exit(1)
        print "Worker exiting, worker %s" % self.name
        return

class Executor(object):
    '''
    Multi-processing task manager, with task queue, pause and halt methods, and callback to finalize once workers are completed
    '''
    def __init__(self, verbose=0):
        self.verbose = verbose
        
        self.status = 'Initialized'
        self.zeroQCount = 0
        self.start_time = -1
        
        # Establish communication and task queues, create consumers
        self.tasks = multiprocessing.Queue() # TODO JoinableQueue()?
        self.completed_pool = multiprocessing.Queue()                        
        self.pauseEvent = multiprocessing.Event()
        self.haltEvent = multiprocessing.Event()
    
    def add_task(self, task):
        self.tasks.put(task)
        
    def get_task_count(self):
        '''
        Returns size the task queue; may be approximate (according to multiprocessing docs)
        Doesn't count the final 'poison pill' tasks in queue
        '''
        if self.get_running_worker_count():
            return self.tasks.qsize() - self.get_running_worker_count()
        else:
            return self.tasks.qsize() - len(self.consumers)
    
    def add_workers(self, num_workers):
        self.consumers = [ Consumer(self.tasks, self.completed_pool, self.pauseEvent, self.haltEvent) for i in xrange(num_workers) ]
        for c in self.consumers:
            self.tasks.put(None)   # add poison pill

    def get_running_worker_count(self):
        return sum([c.is_alive() for c in self.consumers])
    
    def get_running_time(self):
        '''
        Returns the total running time since workers were started
        '''
        if self.start_time==-1: 
            return 0
        else: 
            return time.time() - self.start_time
    
    def has_finished(self):
        '''
        If the task queue is empty, halt all workers
        Return the count of available workers
        '''
        if self.status == 'Initialized': 
            return 0            
        # TODO temporary hack, check if the queue is empty        
        if self.tasks.qsize()==0:
            self.zeroQCount +=1
        if self.zeroQCount>15:
            self.halt_workers()
        
        return not self.get_running_worker_count()>0
    
#    def pauseWorkers(self):
#        self.pauseEvent.set()
#        self.status = 'Paused'
    
    def halt_workers(self):
        for c in self.consumers: 
            c.terminate()          
            # TODO use terminate here or set halt signal?      

    def start_workers(self, status_callback, finalize_callback, test_interval=5):
        '''
        Start workers, handle paused and other states, wait until workers finish to clean up small file downloads
        '''
        if self.status=='Terminated' or self.status=='Completed':
            raise Exception('Cannot resume a ' + self.status + ' session.')
        
        if self.status == 'Initialized':
            self.start_time = time.time()
            for w in self.consumers:
                w.start()
        if self.status == 'Paused':
            self.pauseEvent.clear()
        self.status = 'Running'
        
        # wait until tasks queues are empty, then call finalize callback if all went well
        # TODO use join() method instead of has_finished()
        i=0
        while not self.has_finished():            
            if self.verbose and i: print str(i) + ': ' + status_callback()
            time.sleep(test_interval)
            i+=1
        print "***Workers finished***" # TODO TEMP
        
        if self.get_running_worker_count():
            raise Exception('Error - trying to finalize scheduler when workers are still running.')
        if self.status=='Running':
            # check that all workers completed successfully (first sleep to make sure we're ready)
            time.sleep(1)            
            finalize = True
            while 1:
                try:
                    answer = self.completed_pool.get(False)
                    print "getting worker answer"
                except Queue.Empty:
                    print "completed pool empty, breaking (hopefully exiting)"
                    break
                else:                    
                    if answer.success == False:
                        print "answer failed"
                        finalize = False
                    else:
                        print "answer succeeded"                    
            #for w in self.consumers:
            #    if w.exitcode is None:
            #        raise Exception('Error - at least one process is active when all processes should be terminated')
            #    if w.exitcode != 0:
            #        finalize = False
                    # TODO throw exception when not finalizing? offer cleanup callback (e.g. delete download pieces after failure)?
            if finalize:                              
                finalize_callback()                                            
            self.status = 'Completed'
        else:
            raise Exception('To finalize, the status of the transfer must be "Running."')
        
        #TODO TEST empty task queue
        print "purging task queue"
        while 1:
            try:
                answer = self.tasks.get(False)                
            except Queue.Empty:
                print "completed task queue empty, breaking (hopefully exiting)"
                break
        print "DONE with start_workers"

class MultipartDownload(object):
    '''
    Downloads a (large) file by downloading file parts in separate processes.
    '''
    def __init__(self, api, fileId, local_path, process_count, part_size, temp_dir, start_chunk=1, verbose=0):
        self.api            = api
        self.fileId         = fileId
        self.local_path     = local_path        
        self.part_size      = part_size
        self.process_count  = process_count
        self.verbose        = verbose
        self.temp_dir       = temp_dir
        self.start_chunk    = start_chunk        
        self.setup()
    
    def __str__(self):
        return "MPU - Status: " + self.exe.status +  \
                ", Workers: " + str(self.exe.get_running_worker_count()) + \
                ", Run Time: " + str(self.exe.get_running_time())[:5] + 's' + \
                ", Queue Size: " + str(self.exe.get_task_count()) + \
                ", Percent Completed: " + str(self.task_progress_ratio())[:6] + \
                ", Avg Transfer Rate: " + self.transfer_rate() + \
                ", Data Transferred: " + readable_bytes(self.total_bytes_transfered())
    
    def __repr__(self):
        return str(self)    
    
    def setup(self):
        '''
        Determine number of file pieces to download, add download tasks to work queue 
        '''
        bs_file = self.api.getFileById(self.fileId)
        self.file_name = bs_file.Name
        total_size = bs_file.Size
        self.file_count = int(math.ceil(total_size/self.part_size)) + 1
        
        self.exe = Executor(verbose=self.verbose)                    
        for i in xrange(self.start_chunk,self.file_count+1):         
            t = DownloadTask(self.api, self.fileId, self.file_name, self.local_path, i, self.part_size, total_size, 0, self.temp_dir)
            self.exe.add_task(t)            
        self.exe.add_workers(self.process_count)
        self.task_total = self.exe.get_task_count()
                        
        if self.verbose: 
            print "Total File Size " + str(total_size) + " bytes"
            print "Using Split Size " + str(self.part_size) + " bytes"
            print "File Chunk Count " + str(self.file_count)
            print "Processes " + str(self.process_count)
            print "Start Chunk " + str(self.start_chunk)
            print "Queue Size " + str(self.exe.get_task_count())    
                            
    def start_download(self, test_interval=5):
        '''
        Start download workers
        '''
        status_callback = self.status_update_msg
        finalize_callback = self.combine_file_chunks
        self.exe.start_workers(status_callback, finalize_callback, test_interval)       
        print "DONE DONE with start_download" 
    
    def status_update_msg(self):
        '''
        Callback method to show download status
        '''
        return str(self)
    
    def combine_file_chunks(self):
        '''
        Assembles download files chunks into single large file, then cleanup by deleting file chunks
        '''
        if self.verbose:
                    print "Assembling downloaded file parts into single file"                                                   
        part_files = [os.path.join(self.temp_dir, self.file_name + '.' + str(i)) for i in xrange(self.start_chunk, self.file_count+1)]            
        # TODO check that file exists?
        with open(os.path.join(self.local_path, self.file_name), 'w+b') as whole_file:
            for part_file in part_files:
                shutil.copyfileobj(open(part_file, 'r+b'), whole_file)                         
        for part_file in part_files:
            os.remove(part_file)                        
    
    def transfer_rate(self):
        '''
        Returns transfer rate of download in bytes per second
        '''
        if not self.exe.get_running_time()>0: 
            return '0 b/s'         
        return readable_bytes((self.task_total - self.exe.get_task_count())*self.part_size/self.exe.get_running_time()) + '/s'    
    
    def total_bytes_transfered(self):
        '''
        Returns the total data amount transferred in bytes
        '''        
        return float((self.task_total - self.exe.get_task_count())*self.part_size)
            
    def task_progress_ratio(self):
        '''
        Returns the percent of completed download tasks
        '''
        task_cnt = float(self.exe.get_task_count())
        res = float(self.task_total - task_cnt)/self.task_total
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
    