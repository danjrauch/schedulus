__metaclass__ = type

class Job:
    def __init__(self, id, submit_time, wait, run, used_proc, used_ave_cpu, used_mem, req_proc, req_time, req_mem, status, user_id, group_id, num_exe, num_queue, num_part, num_pre, think_time, start_time=-1, end_time=-1, score=0, state=0, happy=-1, est_start=-1):
        self.id           = id
        self.submit_time  = submit_time
        self.wait         = wait
        self.run          = run
        self.used_proc    = used_proc
        self.used_ave_cpu = used_ave_cpu
        self.used_mem     = used_mem
        self.req_proc     = req_proc
        self.req_time     = req_time
        self.req_mem      = req_mem
        self.status       = status
        self.user_id      = user_id
        self.group_id     = group_id
        self.num_exe      = num_exe
        self.num_queue    = num_queue
        self.num_part     = num_part
        self.num_pre      = num_pre
        self.think_time   = think_time
        self.start_time   = start_time
        self.end_time     = end_time
        self.score        = score
        self.state        = state
        self.happy        = happy
        self.est_start    = est_start

    def submit(self, score=0, est_start=-1):
        self.state = 1
        self.score = score
        self.est_start = est_start
        return 0

    def start(self, time):
        self.state = 2
        self.start = time
        self.wait = time - self.submit_time
        self.end = time + self.run
        return 0

    def finish(self, time=None):
        self.state = 3
        if time:
            self.end = time
        return 0