import pygpao

import time
import os

os.chdir('/Volumes/ESPACE_TRAVAIL_Puma/DANI/RUBEN/rgres_scripts/pygpao/')

@pygpao.job()
def readme():
    file = open("test_fic", "w")
    file.write(f"Il est {time.time()}")
    file.close()

for i in range(3):
    @pygpao.job(
        job=f"job_name_{i}",
        project="test_project",
        args={
            'filename' : f"'mon_fic_{i}'"
        }
    )
    def save_date(filename):
        file = open(filename, "w")
        file.write(f"Il est {time.time()}")
        file.close()

pygpao.send_jobs(api="http://172.24.1.44:8080")