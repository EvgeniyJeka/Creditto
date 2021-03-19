import subprocess
import os
import time
import threading
import logging





if __name__ == '__main__':


    subprocess.run("python ./Matcher/consumer_to_matcher.py")

    subprocess.run("python ./SqlWriter/consumer_to_sql.py")

    subprocess.run("python ./Gateway/gateway.py")

    # threads = list()
    # command_1 = "python ./Gateway/gateway.py"
    # command_2 = "python ./Matcher/consumer_to_matcher.py"
    # command_3 = "python ./SqlWriter/consumer_to_sql.py"
    #
    # logging.info(f"Adding: {command_1}")
    # x = threading.Thread(target=subprocess.run, args=(command_1,))
    # threads.append(x)
    #
    # logging.info(f"Adding: {command_2}")
    # x = threading.Thread(target=subprocess.run, args=(command_2,))
    # threads.append(x)
    #
    # logging.info(f"Adding: {command_3}")
    # x = threading.Thread(target=subprocess.run, args=(command_3,))
    # threads.append(x)
    #
    # for cmnd in threads:
    #     print("Starting new thread")
    #     cmnd.run()


