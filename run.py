from src.application import Application


application = Application()


if __name__ == '__main__':
    try:
        application.run()
    except KeyboardInterrupt:
        application.stop()
