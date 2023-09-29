import io
import uuid
import traceback
from contextlib import redirect_stdout, redirect_stderr
from celery import Celery

from accli import ACliService
from .IamcVerificationService import IamcVerificationService

from configs.Environment import get_environment_variables

env = get_environment_variables()


app = Celery('acc_native_jobs', broker=env.CELERY_BROKER_URL)



def capture_log(func):
    """Capture stdout and stderr to accelerator data repo"""

    def wrapper_func(*args, **kwargs):
        job_token = kwargs['job_token']    
        project_service = ACliService(
            job_token,
            cli_base_url=env.ACCELERATOR_CLI_BASE_URL
        )

        project_service.update_job_status("PROCESSING")

        log_filename = f'{uuid.uuid4().hex}.log'
        log_filepath = f'{log_filename}'

        with open(log_filepath, 'w+') as log_stream:

            with redirect_stdout(log_stream):
                try:
                    func()
                except Exception as err:
                    project_service.update_job_status("ERROR")
                    error_message = ''.join(traceback.format_tb(err.__traceback__))
                    log_stream.write(error_message)

        with open(log_filepath, "rb") as file_stream:
            bucket_object_id = project_service.add_filestream_as_job_output(
                log_filename,
                file_stream
            )
    
        project_service.update_job_status("DONE")

        #TODO @wrufesh delete temp file
        
    return wrapper_func


@app.task
@capture_log
def verify_iamc(*args, **kwargs):
    iamc_verification_service = IamcVerificationService(*args, **kwargs)


@app.task
@capture_log
def merge_iamc(*args, **kwargs):
    iamc_verification_service = IamcVerificationService(*args, **kwargs)
    

    