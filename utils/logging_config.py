import logging
import os
from datetime import datetime

logger = logging.getLogger()

def setup_logging(args):
    log_dir = os.path.join(os.getcwd(), 'logs')
    os.makedirs(log_dir, exist_ok=True)

    date_str = datetime.now().strftime("%Y-%m-%d")
    arg_parts = [str(v) for v in vars(args).values() if v is not None]
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
