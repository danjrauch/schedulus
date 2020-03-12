import simulus
import time
import re
from datetime import datetime
from functools import cmp_to_key 
from src.types.job import *
from src.types.cluster import *


def process_end():



def run(type, backfill, path):
    jobs = []

    with open(path) as job_file:
        for trace_line in job_file:
            # Find string before ';', then split that on whitespace to find trace fields
            job_fields = trace_line.split(';', 1)[0].split()

            if job_fields:
                jobs.append(Job(id=int(job_fields[0]),\
                                submit=float(job_fields[1]),\
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
                                start=-1,\
                                end=-1,\
                                score=0,\
                                state=0,\
                                happy=-1,\
                                est_start=-1))

    for job in jobs:
        print(job.run)

    sim = simulus.simulator()
    sim.sched(process_end, until=10)
    sim.run(100)