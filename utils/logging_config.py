import logging
import os
from datetime import datetime

logger = logging.getLogger()

def setup_logging(args):
    log_dir = os.path.join(os.getcwd(), 'logs')
    os.makedirs(log_dir, exist_ok=True)

    date_str = datetime.now().strftime("%Y-%m-%d")

    def shorten(value, max_len=30):
        if isinstance(value, str) and len(value) > max_len:
            return value[:max_len] + "..."
        return str(value)

    arg_parts = []
    for k, v in vars(args).items():
        if v is not None:
            # names 인자에만 30자 제한 적용
            if k == 'names':
                arg_parts.append(shorten(v))
            else:
                arg_parts.append(str(v))

    arg_part_str = "_".join(arg_parts) if arg_parts else "no_args"
    log_filename = f"{date_str}_{arg_part_str}.log"
    log_path = os.path.join(log_dir, log_filename)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_path),
            logging.StreamHandler()
        ]
    )

    logger.info(f"로그 파일 생성: {log_path}")
