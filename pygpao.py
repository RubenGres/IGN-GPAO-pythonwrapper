import dill
import os
import sys

from gpao.builder import Builder
from gpao.project import Project
from gpao.job import Job

PYTHON_KERNEL_PATH = "env.db"

JOBS = {}

def job(**kwargs):
    global JOBS

    session_path = os.path.abspath(PYTHON_KERNEL_PATH)

    def decorator(func):
        job = kwargs.get("job", f"{func.__name__}_job")
        project = kwargs.get("project", os.path.basename(sys.argv[0]))
        tags = kwargs.get("tags", None)
        args = kwargs.get("args", {})
        
        formatted_args = ', '.join(f'{k}={v}' for k, v in args.items())

        python_command = f'"import dill; dill.load_session(\'{session_path}\'); {func.__name__}({formatted_args})"'
        cmd = f"python3 -c {python_command}"
        cmd = cmd.replace('"', '\\"')
        cmd = f'bash -c "cd {os.getcwd()} && {cmd}"'

        job1 = Job(job, cmd, tags=tags)

        JOBS.setdefault(project, []).append(job1)

        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    
    return decorator


def send_jobs(api, projects_names=None):
    global JOBS

    session_path = os.path.abspath(PYTHON_KERNEL_PATH)

    projects_names = projects_names if projects_names else JOBS.keys()

    projects = []
    for name in projects_names:
        project = Project(name, JOBS[name])
        projects.append(project)

    builder = Builder(projects)
    dill.dump_session(session_path)
    builder.send_project_to_api(api)

    JOBS = {}