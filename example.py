import pygpao

job_names = [f"job_{i}" for i in range(10)]

for name in job_names:
    @pygpao.job(
        name=name,
        project="test",
    )
    def print_yes():
        print('yes')

@pygpao.job(
    name="main",
    project="test",
    deps=job_names,
)
def main():
    print('I think I am becoming dependant...')

pygpao.send_jobs(api="http://172.24.1.44:8080")