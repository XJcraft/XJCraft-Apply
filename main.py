# !/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import logging
import time
import setting
import webbase
import model
import app


if __name__ == "__main__":
    # logger
    if not os.path.exists("logs"):
        os.mkdir("logs")
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(levelname)s]: %(message)s",
                        datefmt="%y-%m-%d %H:%M:%S",
                        filename="logs/%s.log" % time.strftime("%y-%m-%d_%H_%M_%S"),
                        filemode="w")
    sh = logging.StreamHandler()
    sh.setFormatter(logging.getLogger().handlers[0].formatter)
    logging.getLogger().addHandler(sh)

    setting.init()
    model.init()
    app.init()
    webbase.init()
