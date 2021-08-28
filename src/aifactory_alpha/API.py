from aifactory_alpha.Authentification import AFAuth, AFCrypto
from datetime import datetime
from aifactory_alpha.constants import *
import logging
import os
import requests
import http
import json


class AFContest:
    _summary_ = None
    logger = None
    auth_method = None
    user_token = None
    user_email = None
    task_id = None
    model_name_prefix = None
    encrypt_mode = None
    def __init__(self, auth_method=AUTH_METHOD.USERINFO, user_token=None,
                 user_email=None, model_name_prefix=None, task_id=None,
                 log_dir="./log/", debug=False, encrypt_mode=True,
                 submit_url=SUBMISSION_DEFAULT_URL, auth_url=AUTH_DEFAULT_URL):
        self.auth_method = auth_method
        self.refresh_token = user_token
        self.user_email = user_email
        self.model_name_prefix = model_name_prefix
        self.task_id = task_id
        self.set_log_dir(log_dir)
        self.debug = debug
        self.encrypt_mode = encrypt_mode
        self.submit_url = submit_url
        self.auth_url = auth_url
        self.auth_manager = AFAuth(user_email, task_id, self.logger, token=user_token, password=None,
                                   auth_method=auth_method, encrypt_mode=encrypt_mode, auth_url=auth_url, debug=debug)

    def set_log_dir(self, log_dir: str):
        self.log_dir = os.path.abspath(log_dir)
        if not os.path.exists(self.log_dir):
            os.mkdir(self.log_dir)
        if not os.path.isdir(self.log_dir):
            raise AssertionError("{} is not a directory.".format(self.log_dir))
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        stream_handler = logging.StreamHandler()
        formatter = logging.Formatter('%(module)s:%(levelname)s: %(message)s')
        stream_handler.setFormatter(formatter)
        self.logger.addHandler(stream_handler)

    def set_user_email(self, email: str):
        self.user_email = email

    def set_task_id(self, task_id: int):
        self.task_id = task_id

    def set_model_name_prefix(self, model_name_prefix: str):
        self.model_name_prefix = model_name_prefix

    def reset_logger(self, prefix=LOG_TYPE.SUBMISSION):
        cur_log_file_name = prefix+datetime.now().__str__().replace(" ", "-").replace(":", "-").split(".")[0]+".log"
        log_path = os.path.join(self.log_dir, cur_log_file_name)
        file_handler = logging.FileHandler(log_path)
        formatter = logging.Formatter('%(asctime)s:%(module)s:%(levelname)s: %(message)s', '%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        self.log_path = log_path

    def _send_submssion_(self, auth_token, submit_url=SUBMISSION_DEFAULT_URL):
        params = {'token': auth_token}
        response = requests.get(submit_url+'/token', params=params)
        return response

    def submit(self, file):
        # This method submit the answer file to the server.
        def _fail_(self, _status_):
            self.logger.error("Submission Failed.")
            print("Please have a look at the logs in '{}' for more details.".format(self.log_path))
            return _status_
        def _succeed_(self, _status_):
            self.logger.info("Submission was successful.")
            print("Results are recorded in the log file '{}'.".format(self.log_path))
            return _status_
        self.reset_logger(LOG_TYPE.SUBMISSION)
        status = SUBMIT_RESULT.FAIL_TO_SUBMIT
        if not os.path.exists(file):
            self.logger.error("File {} not found.".format(file))
            return status
        auth_token = self.auth_manager.get_token(refresh=True)
        if auth_token is False:
            return _fail_(self, status, log_path)
        self._send_submssion_(auth_token)
        status = SUBMIT_RESULT.SUBMIT_SUCCESS
        return _succeed_(self, status)

    def release(self):
        # This method submit the answer file and the code to the server.
        pass

    def summary(self):
        _summary_ = ">>> Contest Information <<<\n"
        _summary_ += self.auth_manager.summary()
        if self.model_name_prefix is not None:
            _summary_ += "Model Name Prefix: {}\n".format(self.model_name_prefix)
        return _summary_


if __name__ == "__main__":
    c = AFContest(user_email='user0@aifactory.page', task_id='3000', debug=True)
    c.summary()
    c.submit('./sample_data/sample_answer.csv')