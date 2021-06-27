def write_error(error):
    with open('errors.txt', 'a') as f:
        f.write(error)


"""
error.write_error(f"{get_date()} func = check_youtube, status_code = {resp.status_code}")
print('Возникла ошибка при проверки Youtube.\nПауза на 30 минут.')
"""
