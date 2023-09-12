from main import main
import mail_notific
import requests
if __name__ == '__main__':
    try:
        main()
        mail_notific.send_email(3)
    except ConnectionError as ex:
        mail_notific.send_email(2)
        print(ex)
    except ValueError as ex:
        mail_notific.send_email(1)
        print(ex)
    except KeyError as ex:
        mail_notific.send_email(1)
        print(ex)
    except requests.exceptions.ConnectionError as ex:
        mail_notific.send_email(2)
        print(ex)

