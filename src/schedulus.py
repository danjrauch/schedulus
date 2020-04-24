import simulus
import time
import re
import sys
from loguru import logger
from datetime import datetime
from functools import cmp_to_key
from src.types.job import *
from src.types.cluster import *

__metaclass__ = type

class Schedulus:
    def __init__(self, num_proc):
        self.jobs     = {}
        self.schedule = []
        self.waiting  = []
        self.running  = []
        self.cluster  = Cluster(num_proc, num_proc, num_proc)
        self.sim      = simulus.simulator()


    def __log(self, submitted, started, finished):
        if len(self.jobs) <= 10 and (len(self.schedule) <= 1 and len(self.waiting) <= 1 and len(self.running) <= 1):
            logger.debug('<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')
            logger.debug('Time: ' + str(self.sim.now))
            logger.debug('------------------------------')
            logger.debug('Wait: ' + str(self.waiting))
            logger.debug('Run: ' + str(self.running))
            logger.debug('Schedule: ' + str(self.schedule))
            logger.debug('------------------------------')
            logger.debug('Total: ' + str(self.cluster.total) + ' Idle: ' + str(self.cluster.idle))
            logger.debug('------------------------------')
            if submitted:
                logger.debug('[Submit] ' + str(submitted))
            if started:
                logger.debug('[Start] ' + str(started))
            if finished:
                logger.debug('[Finish] ' + str(finished))
            logger.debug('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n')


    def __process_submit(self, job_id, backfill):
        job = self.jobs[job_id]

        job.submit()
        self.waiting.append(job_id)

        if self.cluster.allocate(job.req_proc):
            self.__initiate_job(job_id)
            self.__log([job_id], [job_id], [])
        elif backfill is 'easy':
            self.__backfill(job_id, backfill)
        else:
            self.schedule.append(job_id)
            self.__log([job_id], [], [])

        # if self.cluster.allocate(job.req_proc):
        #     job.start(self.sim.now)
        #     self.sim.sched(self.__process_end, job, until=self.sim.now+job.run)
        #     self.waiting.remove(job.id)
        #     self.running.append(job.id)
        #     self.__log([job.id], [job.id], [])
        # else:
        #     self.schedule.append(job)
        #     self.__log([job.id], [], [])


    def __process_end(self, job_id):
        job = self.jobs[job_id]

        job.finish(self.sim.now)
        self.cluster.release(job.req_proc)
        self.running.remove(job_id)
        started = []
        while self.schedule and self.cluster.allocate(self.jobs[self.schedule[0]].req_proc):
            next_job_id = self.schedule.pop(0)
            self.__initiate_job(next_job_id)
            started.append(next_job_id)
        self.__log([], started, [job_id])


    # https://www.cse.huji.ac.il/~perf/ex11.html
    def __backfill(self, job_id, backfill):
        job = self.jobs[job_id]

        proc_pool = self.cluster.idle
        idle_procs = self.cluster.idle
        extra_procs = 0
        shadow_time = -1

        jobs_exp_end = []
        for r_job_id in self.running:
            # print('Job ' + str(r_job_id) + ' has been running for ' + str(self.sim.now - self.jobs[r_job_id].start_time) + ' seconds')
            # print('Job ' + str(r_job_id) + ' is expected to end at time ' + str(self.jobs[r_job_id].start_time + self.jobs[r_job_id].req_time))
            jobs_exp_end.append((r_job_id, self.jobs[r_job_id].start_time + self.jobs[r_job_id].req_time))
        jobs_exp_end.sort(key=lambda tup: tup[1])

        for job_exp_end in jobs_exp_end:
            if proc_pool < job.req_proc:
                proc_pool += self.jobs[job_exp_end[0]].req_proc
            if proc_pool >= job.req_proc:
                shadow_time = job_exp_end[1]
                extra_procs = proc_pool - job.req_proc

        started = []

        for w_job_id in self.waiting.copy():
            # Condition 1: It uses no more than the currently available processors, and is expected to terminate by the shadow time.
            if self.sim.now + self.jobs[w_job_id].req_time < shadow_time and self.cluster.allocate(self.jobs[w_job_id].req_proc):
                self.__initiate_job(w_job_id)
                started.append(w_job_id)
            # Condition 2: It uses no more than the currently available processors, and also no more than the extra processors.
            elif self.jobs[w_job_id].req_proc <= extra_procs and self.cluster.allocate(self.jobs[w_job_id].req_proc):
                self.__initiate_job(w_job_id)
                extra_procs -= self.jobs[w_job_id].req_proc
                started.append(w_job_id)

        self.schedule.append(job_id)
        self.__log([job_id], started, [])


    def __initiate_job(self, job_id):
        job = self.jobs[job_id]

        job.start(self.sim.now)
        self.sim.sched(self.__process_end, job_id, offset=job.run)
        self.waiting.remove(job_id)
        if job_id in self.schedule:
            self.schedule.remove(job_id)
        self.running.append(job_id)


    def read_jobs(self, path):
        self.jobs = {}

        with open(path) as job_file:
            for trace_line in job_file:
                # Find string before ';', then split that on whitespace to find trace fields
                job_fields = trace_line.split(';', 1)[0].split()

                if job_fields and float(job_fields[3]) != -1:
                    self.jobs[int(job_fields[0])] = Job(id=int(job_fields[0]),\
                                                        submit_time=float(job_fields[1]),\
                                                        wait=float(job_fields[2]),\
                                                        run=float(job_fields[3]),\
                                                        used_proc=int(job_fields[4]),\
                                                        used_ave_cpu=float(job_fields[5]),\
                                                        used_mem=float(job_fields[6]),\
                                                        req_proc=int(job_fields[7]) if int(job_fields[7]) != -1 else int(job_fields[4]),\
                                                        req_time=float(job_fields[8]),\
                                                        req_mem=float(job_fields[9]),\
                                                        status=int(job_fields[10]),\
                                                        user_id=int(job_fields[11]),\
                                                        group_id=int(job_fields[12]),\
                                                        num_exe=int(job_fields[13]),\
                                                        num_queue=int(job_fields[14]),\
                                                        num_part=int(job_fields[15]),\
                                                        num_pre=int(job_fields[16]),\
                                                        think_time=int(job_fields[17]),\
                                                        start_time=-1,\
                                                        end_time=-1,\
                                                        score=0,\
                                                        state=0,\
                                                        happy=-1,\
                                                        est_start=-1)

    def run(self, type, backfill):
        logger.remove()
        logger.add(sys.stdout, format='{message}', level='DEBUG')

        for job in self.jobs.values():
            self.sim.sched(self.__process_submit, job.id, backfill, until=job.submit_time)
            # self.sim.process(self.__process_submit, job, until=job.submit_time, prio=job.id)

        self.sim.run()

        for job in self.jobs.values():
            print('Bounded Slowdown for job ID : ' + str(job.id) + ' = ' + str(max((job.wait+(job.end-job.start_time)) / max((job.end-job.start_time), 10), 1)))