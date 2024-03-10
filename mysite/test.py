import time


@background(schedule=0)
def listen_to_rabbitmq():
    print("in the listening")



async def consume():
    time.sleep(5)
    print("in the consume")


if __name__ == '__main__':
    listen_to_rabbitmq()
    for i in range(10):
        print(i)
