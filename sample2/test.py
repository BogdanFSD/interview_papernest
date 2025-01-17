from celery.result import AsyncResult
task_id = "829a6c33-9fbd-494a-9d84-b50da42d0f1b"  # Replace with the actual ID
result = AsyncResult(task_id)
print(result.status)  # Should be "SUCCESS" if it executed
print(result.result)  # Output of the task, if any
