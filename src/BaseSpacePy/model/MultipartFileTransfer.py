
import time
import os
import math
import multiprocessing
import Queue
import shutil
import signal
import hashlib
from subprocess import call
import logging
from BaseSpacePy.api.BaseSpaceException import MultiProcessingTaskFailedException

LOGGER = logging.getLogger(__name__)

class UploadTask(object):
    '''
    Uploads a piece of a large local file.    
    '''    
    def __init__(self, api, bs_file_id, piece, total_pieces, local_path, total_size, temp_dir):
        self.api        = api
        self.bs_file_id = bs_file_id  # the BaseSpace File Id
        self.piece      = piece       # piece number 
        self.total_pieces = total_pieces # out of total piece count
        self.local_path = local_path  # the path of the local file to be uploaded, including file name        
        self.total_size = total_size  # total file size of upload, for reporting
        self.temp_dir   = temp_dir    # temp location to store file chunks for upload
        
        # tasks must implement these attributes and execute()
        self.success  = False
        self.err_msg = "no error"      
    
    def execute(self, lock):
        '''
        Upload a piece of the target file, first splitting the local file into a temp file.
        Calculate md5 of file piece and pass to upload method.
        Lock is not used (but needed since worker sends it for multipart download)
        '''            
        try:
            fname = os.path.basename(self.local_path)
            # this relies on the way the calling function has split the file
            # but we still need to pass around the piece numbers because the BaseSpace API needs them
            # to reassemble the file at the other end
            # the zfill(4) is to make sure we have a zero padded suffix that split -a 4 -d will make
            transFile = os.path.join(self.temp_dir, fname + str(self.piece).zfill(4))
            #cmd = ['split', '-d', '-n', str(self.piece) + '/' + str(self.total_pieces), self.local_path]                        
            #with open(transFile, "w") as fp:                                                    
            #    rc = call(cmd, stdout=fp)
            #    if rc != 0:
            #        self.sucess = False
            #        self.err_msg = "Splitting local file failed for piece %s" % str(self.piece)
            #        return self            
            with open(transFile, "r") as f:
                out = f.read()
                self.md5 = hashlib.md5(out).digest().encode('base64')            
            try:
                res = self.api.__uploadMultipartUnit__(self.bs_file_id,self.piece+1,self.md5,transFile)
            except Exception as e:
                self.success = False
                self.err_msg = str(e)                
            else:
                # ETag contains hex encoded MD5 of part data on success
                if res and res['Response'].has_key('ETag'):                
                    self.success = True
                else:
                    self.success = False
                    self.err_msg = "Error - empty response from uploading file piece or missing ETag in response"
            if self.success:
                os.remove(transFile)
        # capture exception, since unpickleable exceptions may block
        except Exception as e:
            self.success = False
            self.err_msg = str(e)
        return self
        
    def __str__(self):
        return 'File piece %d of %d, total file size %s' % (self.piece, self.total_pieces, Utils.readable_bytes(self.total_size))


class DownloadTask(object):
    '''
    Downloads a piece of a large remote file.
    When temp_dir is set (debug mode), downloads to filename with piece number appended (i.e. temp file).
    '''    
    def __init__(self, api, bs_file_id, file_name, local_dir, piece, total_pieces, part_size, total_size, temp_dir=None):
        self.api = api                # BaseSpace api object
        self.bs_file_id = bs_file_id  # the Id of the File in BaseSpace
        self.file_name = file_name    # the name of the file to download
        self.piece  = piece           # piece number
        self.total_pieces = total_pieces # total pieces being downloaded (for reporting only)
        self.part_size = part_size    # the size in bytes (not MB) of each piece (except last piece)
        self.total_size  = total_size # the total size of the file in bytes
        self.local_dir = local_dir    # the path in which to store the downloaded file        
        self.temp_dir = temp_dir      # optional: set temp_dir for debug mode, which writes downloaded chunks to individual temp files         
        
        # tasks must implement these attributes and execute()
        self.success  = False
        self.err_msg = "no error"         
    
    def execute(self, lock):
        '''
        Download a piece of the target file, first calculating start/end bytes for piece.
        Lock is to ensure that multiple processes don't write to same file concurrently.
        '''
        try:
            if self.temp_dir:
                #transFile = os.path.join(self.temp_dir, self.file_name + "." + str(self.piece))
                local_dir = self.temp_dir
                local_name = self.file_name + "." + str(self.piece)
                standaloneRangeFile = True
            else:
                #transFile = os.path.join(self.temp_dir, self.file_name)
                local_dir = self.local_dir
                local_name = self.file_name
                standaloneRangeFile = False
            startbyte = (self.piece - 1) * self.part_size
            endbyte = (self.piece * self.part_size) - 1
            if endbyte > self.total_size:
                endbyte = self.total_size - 1            
            try:                
                #self.api.__downloadFile__(self.bs_file_id, self.local_dir, transFile, [startbyte, endbyte], standaloneRangeFile, lock)
                self.api.__downloadFile__(self.bs_file_id, local_dir, local_name, [startbyte, endbyte], standaloneRangeFile, lock)                                
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
        return 'File piece %d of %d, piece size %s of total %s' % (self.piece, self.total_pieces, Utils.readable_bytes(self.part_size), Utils.readable_bytes(self.total_size))
    
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
        new tasks. 
        
        For download tasks, use lock to ensure sole access (among worker
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
                    answer = next_task.execute(self.lock) # acquired lock will block other workers                                       
                    if answer.success == True:
                        self.task_queue.task_done()                   
                        self.result_queue.put(True)
                        break
                    else:
                        LOGGER.debug("Worker %s retrying task %s after failure, retry attempt %d, with error msg: %s" % (self.name, str(next_task), i, answer.err_msg))
                        time.sleep(self.retry_wait)                    
                if not answer.success == True:
                    LOGGER.debug("Worker %s exiting, too many failures with retry for worker %s" % (self.name, str(self)))
                    LOGGER.warning("Task failed after too many retries")        
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
    Multi-processing task manager, with callback to finalize once workers are completed.
    Task queue contains tasks, with poison pill for each worker.
    Result queue contains True/False results for task success/failure.
    Halt event will tell workers to halt themselves.
    
    For downloads, lock is to ensure that only one worker writes to a local downloaded file at a time. 
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
            self.tasks.join() # wait for workers to finish current work then exit from response to halt signal
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
                    LOGGER.debug("Found a failed or cancelled task -- won't call finalize callback")
                    finalize = False                                            
        if finalize == True:                              
            finalize_callback()
        else:            
            raise MultiProcessingTaskFailedException("Multiprocessing task did not complete successfully")                                                 

class MultipartUpload(object):
    '''
    Uploads a (large) file by uploading file parts in separate processes.    
    '''
    def __init__(self, api, local_path, bs_file, process_count, part_size, temp_dir):
        '''
        Create a multipart upload object
        
        :param api:           the BaseSpace API object        
        :param local_path:    the path of the local file, including file name
        :param bs_file:       the File object of the newly created BaseSpace File to upload 
        :param process_count: the number of process to use for uploading
        :param part_size:     in MB, the size of each uploaded part        
        :param temp_dir:      temp directory to store file pieces for upload 
        '''
        self.api            = api    
        self.local_path     = local_path    
        self.remote_file    = bs_file
        self.process_count  = process_count
        self.part_size      = part_size
        self.temp_dir       = temp_dir               
                                           
        self.start_chunk    = 0
    
    def upload(self):
        '''
        Start the upload, then when complete retrieve and return the file object from
        BaseSpace that has updated (completed) attributes.
        '''
        self._setup()
        self._start_workers()        
        return self.api.getFileById(self.remote_file.Id)                        
    
    def _setup(self):        
        '''
        Determine number of file pieces to upload, add upload tasks to work queue         
        '''                
        logfile = os.path.join(self.temp_dir, "main.log")
        total_size = os.path.getsize(self.local_path)        
        fileCount = int(total_size/(self.part_size*1024*1024)) + 1

        chunk_size = (total_size / fileCount) + 1
        assert chunk_size * fileCount > total_size

        fname = os.path.basename(self.local_path)
        prefix = os.path.join(self.temp_dir, fname)
        # -a 4  always use 4 digit sufixes, to make sure we can predict the filenames
        # -d    use digits as suffixes, not letters
        # -b    chunk size (in bytes)
        cmd = ['split', '-a', '4', '-d', '-b', str(chunk_size), self.local_path, prefix]
        rc = call(cmd)
        if rc != 0:
            err_msg = "Splitting local file failed: %s" % str.local_path
            raise MultiProcessingTaskFailedException(err_msg)

        self.exe = Executor()                    
        for i in xrange(self.start_chunk, fileCount):
            t = UploadTask(self.api, self.remote_file.Id, i, fileCount, self.local_path, total_size, self.temp_dir)            
            self.exe.add_task(t)            
        self.exe.add_workers(self.process_count)
        self.task_total = fileCount - self.start_chunk + 1                                                

        LOGGER.info("Total File Size %s" % Utils.readable_bytes(total_size))
        LOGGER.info("Using File Part Size %d MB" % self.part_size)
        LOGGER.info("Processes %d" % self.process_count)
        LOGGER.info("File Chunk Count %d" % self.task_total)
        LOGGER.info("Start Chunk %d" % self.start_chunk)    

    def _start_workers(self):
        '''
        Start upload workers, register finalize callback method
        '''                
        finalize_callback = self._finalize_upload # lambda: None            
        self.exe.start_workers(finalize_callback)
    
    def _finalize_upload(self):
        '''
        Set file upload status as complete in BaseSpace
        '''
        LOGGER.debug("Marking uploaded file status as complete")                                                   
        self.api.__finalizeMultipartFileUpload__(self.remote_file.Id)

class MultipartDownload(object):
    '''
    Downloads a (large) file by downloading file parts in separate processes.
    When temp_dir is set (debug mode), downloads chunks to individual temp files, then cats them together.
    Returns File object when complete.
    '''
    def __init__(self, api, file_id, local_dir, process_count, part_size, create_bs_dir, temp_dir=""):
        '''
        Create a multipart download object
        
        :param api:           the BaseSpace API object
        :param file_id:       the BaseSpace File Id of the file to download
        :param local_dir:     the local directory in which to store the downloaded file
        :param process_count: the number of process to use for downloading
        :param part_size:     in MB, the size of each file part to download        
        :param create_bs_dir: when True, create BaseSpace File's directory in local_dir; when False, ignore Bs directory
        :param temp_dir:      (optional) temp directory for debug mode        
        '''
        self.api            = api            
        self.file_id        = file_id         
        self.local_dir      = local_dir               
        self.process_count  = process_count  
        self.part_size      = part_size              
        self.temp_dir       = temp_dir
        self.create_bs_dir  = create_bs_dir        

        self.start_chunk      = 1        
        self.partial_file_ext = ".partial"
    
    def download(self):
        '''
        Start the download
        '''
        self._setup()
        self._start_workers()
        return self.bs_file                
        
    def _setup(self):
        '''
        Determine number of file pieces to download, determine full local path
        in which to download file, add download tasks to work queue.
        
        While download is in progress, name the file with a 'partial' extension 
        '''
        self.bs_file = self.api.getFileById(self.file_id)
        self.file_name = self.bs_file.Name
        total_bytes = self.bs_file.Size
        part_size_bytes = self.part_size * (1024**2)
        self.file_count = int(math.ceil(total_bytes/part_size_bytes)) + 1
        
        file_name = self.file_name
        if not self.temp_dir:
            file_name = self.file_name + self.partial_file_ext

        self.full_local_dir = self.local_dir
        self.full_temp_dir = self.temp_dir
        if self.create_bs_dir:            
            self.full_local_dir = os.path.join(self.local_dir, os.path.dirname(self.bs_file.Path))            
            if not os.path.exists(self.full_local_dir):
                os.makedirs(self.full_local_dir)
            if self.temp_dir:
                self.full_temp_dir = os.path.join(self.temp_dir, os.path.dirname(self.bs_file.Path))
                if not os.path.exists(self.full_temp_dir):
                    os.makedirs(self.full_temp_dir)
        
        self.exe = Executor()                    
        for i in xrange(self.start_chunk, self.file_count+1):         
            t = DownloadTask(self.api, self.file_id, file_name, self.full_local_dir, 
                             i, self.file_count, part_size_bytes, total_bytes, self.full_temp_dir)
            self.exe.add_task(t)            
        self.exe.add_workers(self.process_count)        
        self.task_total = self.file_count - self.start_chunk + 1                                                
                                 
        LOGGER.info("Total File Size %s" % Utils.readable_bytes(total_bytes))
        LOGGER.info("Using File Part Size %s MB" % str(self.part_size))
        LOGGER.info("Processes %d" % self.process_count)
        LOGGER.info("File Chunk Count %d" % self.file_count)
        LOGGER.info("Start Chunk %d" % self.start_chunk)
                            
    def _start_workers(self):
        '''
        Start download workers, register finalize callback method
        '''        
        if self.temp_dir:
            finalize_callback = self._combine_file_chunks
        else:
            finalize_callback = self._rename_final_file # lambda: None            
        self.exe.start_workers(finalize_callback)                        
    
    def _rename_final_file(self):
        '''
        Remove the 'partial' extension from the downloaded file
        '''
        final_file = os.path.join(self.full_local_dir, self.file_name)
        partial_file = final_file + self.partial_file_ext
        os.rename(partial_file, final_file) 
    
    def _combine_file_chunks(self):
        '''
        Assembles download files chunks into single large file, then cleanup by deleting file chunks
        '''        
        LOGGER.debug("Assembling downloaded file parts into single file")                                                   
        part_files = [os.path.join(self.full_temp_dir, self.file_name + '.' + str(i)) for i in xrange(self.start_chunk, self.file_count+1)]                    
        with open(os.path.join(self.full_local_dir, self.file_name), 'w+b') as whole_file:
            for part_file in part_files:                
                shutil.copyfileobj(open(part_file, 'r+b'), whole_file)                         
        for part_file in part_files:
            os.remove(part_file)                        

class Utils(object):
    '''
    Utility methods for multipartDownload classes
    '''
    @staticmethod
    def md5_for_file(f, block_size=1024*1024):
        '''
        Returns the md5 for the provided file (must have been opened in binary mode)
        '''
        md5 = hashlib.md5()
        while True:
            data = f.read(block_size)
            if not data:
                break
            md5.update(data)
        return md5.hexdigest()
    
    @staticmethod
    def readable_bytes(size, precision=2):
        """
        Utility function to display number of bytes in a human-readable form; BaseSpace uses the Base 2 definition of bytes
        """
        suffixes=['B','KB','MB','GB','TB']
        suffixIndex = 0
        while size > 1024:
            suffixIndex += 1 # increment the index of the suffix
            size = size / 1024.0 # apply the division
        return "%.*f %s" % (precision, size, suffixes[suffixIndex])
        