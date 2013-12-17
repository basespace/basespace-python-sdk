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
import signal
import hashlib
import logging

LOGGER = logging.getLogger(__name__)


class DownloadTask(object):
    '''
    Downloads a piece of a large remote file.
    In debug mode downloads to filename with piece number appended (i.e. temp file).
    '''    
    def __init__(self, api, bs_file_id, file_name, local_path, piece, part_size, total_size, temp_dir=None, debug=False):
        self.api = api                # BaseSpace api object
        self.bs_file_id = bs_file_id  # the baseSpace fileId
        self.file_name = file_name    # the name of the file to download
        self.piece  = piece           # piece number
        self.part_size = part_size    # the size in bytes of each piece (except last piece)
        self.total_size  = total_size # the total size of the file in bytes
        self.local_path = local_path  # the path in which to store the downloaded file        
        self.temp_dir = temp_dir      # temp dir for debug mode
        self.debug = debug            # debug mode writes downloaded chunks to individual temp files
        
        # tasks must implement these attributes
        self.success  = False
        self.err_msg = "no error"         
    
    def __call__(self):
        '''
        Download a piece of the target file, first calculating start/end bytes for piece.
        '''
        try:
            if self.debug:
                transFile = os.path.join(self.temp_dir, self.file_name + "." + str(self.piece))
                standaloneRangeFile = True
            else:
                transFile = os.path.join(self.temp_dir, self.file_name)
                standaloneRangeFile = False
            startbyte = (self.piece - 1) * self.part_size
            endbyte = (self.piece * self.part_size) - 1
            if endbyte > self.total_size:
                endbyte = self.total_size - 1
            try:                                                
                self.api.fileDownload(self.bs_file_id, self.local_path, transFile, [startbyte, endbyte], standaloneRangeFile)                                
            except Exception as e:
                self.success = False
                self.err_msg = str(e)                
            else:                
                self.success = True
        # capture exception, since unpickleable exceptions may block
        except Exception as e:
            self.success = False
            self.err_msg = str(e)
        return self
        
    def __str__(self):                
        return 'File piece %s, piece size %s' % (self.piece, self.part_size)
    
class Consumer(multiprocessing.Process):
    '''
    Multi-processing worker that executes tasks from task queue with retry
    On failure after retries, alerts all workers to halt
    '''
    
    def __init__(self, task_queue, result_queue, halt_event, lock):    
        multiprocessing.Process.__init__(self)
        self.task_queue = task_queue
        self.result_queue = result_queue        
        self.halt = halt_event
        self.lock = lock         
        
        self.get_task_timeout = 5 # secs
        self.retry_wait = 1 # sec
        self.retries = 20
        
    def run(self):
        '''
        Executes tasks from the task queue until poison pill is reached, halt 
        signal is found, or something went wrong such as a timeout when getting
        new tasks. Use lock, for download tasks, to ensure sole access (among worker
        processes) to downloaded file.
        
        Retries failed tasks, and add task results to result_queue.
        When a task fails for all retries, set halt signal to alert other workers
        and purge task queue or remaining tasks (to unblock join() in parent process)
        
        Turn off SIGINT (Ctrl C), handle in parent process
        '''
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        while True:                                
            try:
                next_task = self.task_queue.get(True, self.get_task_timeout) # block until timeout
            except Queue.Empty:
                LOGGER.debug('Worker %s exiting, getting task from task queue timed out and/or is empty' % self.name)
                break                    
            if next_task is None:            
                LOGGER.debug('Worker %s exiting, found final task' % self.name)
                self.task_queue.task_done()
                break                                                                   
            else:                                                       
                # attempt to run tasks, with retry
                LOGGER.debug('Worker %s processing task: %s' % (self.name, str(next_task)))
                for i in xrange(1, self.retries + 1):                        
                    if self.halt.is_set():
                        LOGGER.debug('Worker %s exiting, found halt signal' % self.name)
                        self.task_queue.task_done()
                        self.purge_task_queue()
                        return
                    with self.lock:
                        answer = next_task()                                        
                    if answer.success == True:
                        self.task_queue.task_done()                   
                        self.result_queue.put(True)
                        break
                    else:
                        LOGGER.debug("Worker %s retrying task %s after failure, retry attempt %d, with error msg: %s" % self.name, str(next_task), i,  answer.err_msg)
                        time.sleep(self.retry_wait)                    
                if not answer.success == True:
                    LOGGER.debug("Worker %s exiting, too many failures with retry for worker %s" % self.name, str(self))
                    LOGGER.warning("Download failed after too many retries")        
                    self.task_queue.task_done()                   
                    self.result_queue.put(False)
                    self.purge_task_queue() # purge task queue in case there's only one worker                    
                    self.halt.set()
                    break        
        return
    
    def purge_task_queue(self):
        '''
        Purge all remaining tasks from task queue. This will also remove poison pills
        (final tasks), so run() must handle an empty queue (by using a timeout with
        task_queue.get() ).
        '''        
        LOGGER.debug("Purging task queue")
        while 1:
            try:
                self.task_queue.get(False)                
            except Queue.Empty:            
                break
            else:
                self.task_queue.task_done()
                
class Executor(object):
    '''
    Multi-processing task manager, with callback to finalize once workers are completed
    Task queue contains tasks, with poison pill for each worker
    Result queue contains True/False results for task success/failure
    Halt event will tell workers to halt themselves
    Lock is to ensure that only one worker writes to a local (downloaded) file at a time 
    '''
    def __init__(self):                                        
        self.tasks = multiprocessing.JoinableQueue()
        self.result_queue = multiprocessing.Queue()                        
        self.halt_event = multiprocessing.Event()
        self.lock = multiprocessing.Lock()
    
    def add_task(self, task):
        '''
        Add task to task queue
        '''
        self.tasks.put(task)        
    
    def add_workers(self, num_workers):
        '''
        Added workers to internal list of workers, adding a poison pill for each to the task queue
        '''
        self.consumers = [ Consumer(self.tasks, self.result_queue, self.halt_event, self.lock) for i in xrange(num_workers) ]
        for c in self.consumers:
            self.tasks.put(None)

    def start_workers(self, finalize_callback):
        '''
        Start workers, wait until workers finish, then call finalize callback if all went well
        '''        
        # TODO add failure callback for cleanup?
        for w in self.consumers:
            w.start()        
        LOGGER.debug("Workers started")                
        try:
            self.tasks.join()
        except (KeyboardInterrupt, SystemExit):
            LOGGER.debug("Halting all workers -- received exit signal")
            self.result_queue.put(False)
            self.halt_event.set()
        else:                        
            LOGGER.debug("Workers finished - task queue joined")                                   
        finalize = True
        while 1:
            try:
                success = self.result_queue.get(False) # non-blocking                    
            except Queue.Empty:                    
                break
            else:                    
                if success == False:                        
                    LOGGER.debug("Found a failed task -- won't call finalize callback")
                    finalize = False                                            
        if finalize:                              
            finalize_callback()                                                                

class MultipartDownload(object):
    '''
    Downloads a (large) file by downloading file parts in separate processes.
    Debug mode downloads chunks to individual temp files, then cats them together
    '''
    def __init__(self, api, fileId, local_path, process_count, part_size, start_chunk=1, temp_dir=None, debug=False):
        self.api            = api
        self.fileId         = fileId
        self.local_path     = local_path        
        self.part_size      = part_size
        self.process_count  = process_count
        self.temp_dir       = temp_dir
        self.start_chunk    = start_chunk
        self.debug          = debug                   
        self.setup()
        self.start_download()
        
    def setup(self):
        '''
        Determine number of file pieces to download, add download tasks to work queue 
        '''
        bs_file = self.api.getFileById(self.fileId)
        self.file_name = bs_file.Name
        total_size = bs_file.Size
        self.file_count = int(math.ceil(total_size/self.part_size)) + 1
        
        self.exe = Executor()                    
        for i in xrange(self.start_chunk,self.file_count+1):         
            t = DownloadTask(self.api, self.fileId, self.file_name, self.local_path, i, self.part_size, total_size, self.temp_dir, self.debug)
            self.exe.add_task(t)            
        self.exe.add_workers(self.process_count)
        self.task_total = self.file_count                
                                 
        LOGGER.info("Total File Size %d bytes" % total_size)
        LOGGER.info("Using Split Size %d bytes" % self.part_size)
        LOGGER.info("File Chunk Count %d" % self.file_count)
        LOGGER.info("Processes %d" % self.process_count)
        LOGGER.info("Start Chunk %d" % self.start_chunk)
                            
    def start_download(self):
        '''
        Start download workers, register finalize callback method
        '''        
        if self.debug:
            finalize_callback = self.combine_file_chunks
        else:
            finalize_callback = lambda: None            
        self.exe.start_workers(finalize_callback)                        
    
    def combine_file_chunks(self):
        '''
        Assembles download files chunks into single large file, then cleanup by deleting file chunks
        '''        
        LOGGER.debug("Assembling downloaded file parts into single file")                                                   
        part_files = [os.path.join(self.temp_dir, self.file_name + '.' + str(i)) for i in xrange(self.start_chunk, self.file_count+1)]            
        # TODO check that file exists?
        with open(os.path.join(self.local_path, self.file_name), 'w+b') as whole_file:
            for part_file in part_files:
                shutil.copyfileobj(open(part_file, 'r+b'), whole_file)                         
        for part_file in part_files:
            os.remove(part_file)                        


    
def md5_for_file(f, block_size=1024*1024):
    '''
    Returns the md5 for the provided file (opened in binary mode)
    (not currently used)
    '''
    md5 = hashlib.md5()
    while True:
        data = f.read(block_size)
        if not data:
            break
        md5.update(data)
    return md5.hexdigest()

def readable_bytes(size, precision=2):
    """
    Utility function to display number of bytes in a human-readable form; BaseSpace uses the Base 2 definition of bytes
    (not currently used)
    """
    suffixes=['B','KB','MB','GB','TB']
    suffixIndex = 0
    while size > 1024:
        suffixIndex += 1 # increment the index of the suffix
        size = size / 1024.0 # apply the division
    return "%.*f %s"%(precision, size, suffixes[suffixIndex])
    