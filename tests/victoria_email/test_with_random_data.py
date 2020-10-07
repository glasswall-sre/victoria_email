import uuid
import tempfile
import os
import random
from os import listdir
import aiorun
from victoria_email import load_test, schemas

available_formats = ['bmp', 'doc', 'docx', 'emf', 'gif', 'jpg', 'mp3', 'mp4', 'mpg', 'pdf', 'png', 'ppt', 'pptx', 'tif',
                     'wav', 'wmf', 'xls', 'xlsx']


def generate_random_uuid() -> list:
    uuid_list = [str(uuid.uuid4()) for _ in range(20)]
    return uuid_list


def generate_random_files(tmpdirname: str) -> list:
    for i in range(20):
        with open(f'{tmpdirname}/test-{i}.{random.choice(available_formats)}', 'wb') as file:
            file.write(os.urandom(1024 * random.randint(1, 100)))
    files = list()
    for name in listdir(tmpdirname):
        file = dict()
        path = f'{tmpdirname}/{name}'
        file['file'] = path
        file['weight'] = os.path.getsize(path)
        files.append(file)
    return files


def generate_random_config(tmpdirname: str) -> schemas.EmailConfig:
    config = {
        'load_test':
            {
                'mail_send_function_endpoint': 'http://localhost:7071/api/send',
                'mail_send_function_code': 'unittest',
                'tenant_ids': generate_random_uuid(),
                'timeout': 10.0,
                'load': {
                    'distribution': generate_random_files(tmpdirname),
                    'attachment_count': [12, 30],
                }
            }
    }
    email_schema = schemas.EmailConfigSchema()
    email_config = email_schema.load(config)
    return email_config


def perform_test(cfg: schemas.EmailConfig, frequency: int, endpoint: str,
                 duration: int, recipient: str, sender: str) -> None:
    loop = aiorun.get_event_loop()
    loop.set_exception_handler(lambda loop, context: "Error")
    loop.run_until_complete(
        load_test.perform_load_test(frequency, endpoint, duration, recipient,
                                    sender, cfg.load_test))


def email_load_test() -> None:
    with tempfile.TemporaryDirectory() as tmpdirname:
        config = generate_random_config(tmpdirname)
        perform_test(frequency=10, endpoint='0.0.0.0:25', duration=10, recipient='test@example.com',
                     sender='test@example.com', cfg=config)


if __name__ == '__main__':
    email_load_test()
