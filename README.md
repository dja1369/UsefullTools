# SimpleLogger
this is Simple Python Logger!

```
def custom_logger(position: str, level: str):
    """
    Logger name 'position'
    Logger lavel 'level'
        'CRITICAL': CRITICAL,
        'FATAL': FATAL,
        'ERROR': ERROR,
        'WARN': WARNING,
        'WARNING': WARNING,
        'INFO': INFO,
        'DEBUG': DEBUG,
        'NOTSET': NOTSET,
    """
    path = os.getcwd() + "/log"
    if not os.path.exists(path):
        os.makedirs(path, )
    logger: Logger = getLogger(position)
    logger.setLevel(level)

    formatter: Formatter = Formatter(
        'Time: %(asctime)-19s Call: %(name)s \n\t - Level: %(levelname)-s - MSG: %(message)s')
    stream_handler: StreamHandler = StreamHandler()
    stream_handler.setFormatter(formatter)

    file_handler: FileHandler = FileHandler(filename=(path + "/" + str(datetime.now().date())
                                                      + "_" + position + ".log"), mode="a")
    file_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

    return logger


# Use It!
if __name__ == '__main__':
    logger = custom_logger(position="test", level="DEBUG")
    logger.info("test")
```
