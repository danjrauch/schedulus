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
        self.jobs     = []
        self.schedule = []
        self.waiting  = []
        self.running  = []
        self.cluster  = Cluster(num_proc, num_proc, num_proc)
        self.sim      = simulus.simulator()


    def __log(self, submitted, started, finished):
        logger.debug('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
        logger.debug('Time: ' + str(self.sim.now))
        logger.debug('------------------------------')
        logger.debug('Wait: ' + str(self.waiting))
        logger.debug('Run: ' + str(self.running))
        logger.debug('------------------------------')
        logger.debug('Total: ' + str(self.cluster.total) + ' Idle: ' + str(self.cluster.idle))
        logger.debug('------------------------------')
        if submitted:
            logger.debug('[Submit] ' + str(submitted))
        if started:
            logger.debug('[Start] ' + str(started))
        if finished:
            logger.debug('[Finish] ' + str(finished))
        logger.debug('<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n')


    def __process_submit(self, job):
        job.submit()
        self.waiting.append(job.id)

        if not self.running and self.cluster.allocate(job.req_proc):
            job.start(self.sim.now)
            self.sim.sched(self.__process_end, job, offset=job.run)
            # self.sim.process(self.__process_end, job, offset=job.run, prio=0)
            self.waiting.remove(job.id)
            self.running.append(job.id)
            self.__log([job.id], [job.id], [])
        else:
            self.schedule.append(job)
            self.__log([job.id], [], [])

        # if self.cluster.allocate(job.req_proc):
        #     job.start(self.sim.now)
        #     self.sim.sched(self.__process_end, job, until=self.sim.now+job.run)
        #     self.waiting.remove(job.id)
        #     self.running.append(job.id)
        #     self.__log([job.id], [job.id], [])
        # else:
        #     self.schedule.append(job)
        #     self.__log([job.id], [], [])


    def __process_end(self, job):
        job.finish(self.sim.now)
        self.cluster.release(job.req_proc)
        self.running.remove(job.id)
        started = []
        finished = [job.id]
        while self.schedule and self.cluster.allocate(self.schedule[0].req_proc):
            next_job = self.schedule.pop(0)
            next_job.start(self.sim.now)
            self.sim.sched(self.__process_end, next_job, offset=next_job.run)
            # self.sim.process(self.__process_end, next_job, offset=next_job.run, prio=0)
            self.waiting.remove(next_job.id)
            self.running.append(next_job.id)
            started.append(next_job.id)
        self.__log([], started, finished)


    def read_jobs(self, path):
        self.jobs = []

        with open(path) as job_file:
            for trace_line in job_file:
                # Find string before ';', then split that on whitespace to find trace fields
                job_fields = trace_line.split(';', 1)[0].split()

                if job_fields:
                    self.jobs.append(Job(id=int(job_fields[0]),\
                                         submit_time=float(job_fields[1]),\
                                         wait=float(job_fields[2]),\
                                         run=float(job_fields[3]),\
                                         used_proc=int(job_fields[4]),\
                                         used_ave_cpu=float(job_fields[5]),\
                                         used_mem=float(job_fields[6]),\
                                         req_proc=int(job_fields[7]),\
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
                                         est_start=-1))

    def run(self, type, backfill):
        logger.remove()
        logger.add(sys.stderr, format='{message}', level='DEBUG')

        for job in self.jobs:
            self.sim.sched(self.__process_submit, job, until=job.submit_time)
            # self.sim.process(self.__process_submit, job, until=job.submit_time, prio=job.id)

        self.sim.run()